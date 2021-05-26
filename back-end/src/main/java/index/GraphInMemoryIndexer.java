package index;

import com.github.davidmoten.rtree.Entry;
import com.github.davidmoten.rtree.RTree;
import com.github.davidmoten.rtree.geometry.Geometries;
import com.github.davidmoten.rtree.geometry.Rectangle;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.InputStreamReader;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Locale;
import java.util.List;
import main.Config;
import main.DbConnector;
import main.Main;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;
import project.Canvas;
import project.Layer;
import project.Graph;
import vlsi.utils.CompactHashMap;

/** Created on 3/13/21. */
public class GraphInMemoryIndexer extends PsqlNativeBoxIndexer {
    private class RTreeData {
        int rowId;
        float minx, miny, maxx, maxy;
        CompactHashMap<String, Float> numericalAggs;
        float[][] convexHull;
        int[] topk;

        RTreeData(int _rowId) {
            rowId = _rowId;
            minx = miny = maxx = maxy = 0;
            numericalAggs = null;
            convexHull = null;
            topk = null;
        }

        public RTreeData clone() {
            RTreeData ret = new RTreeData(rowId);
            if (numericalAggs != null) {
                ret.numericalAggs = new CompactHashMap<>();
                for (String key : numericalAggs.keySet())
                    ret.numericalAggs.put(key, numericalAggs.get(key));
            }
            if (convexHull != null) {
                ret.convexHull = new float[convexHull.length][2];
                for (int i = 0; i < convexHull.length; i++) {
                    ret.convexHull[i][0] = convexHull[i][0];
                    ret.convexHull[i][1] = convexHull[i][1];
                }
            }
            if (topk != null) {
                ret.topk = new int[topk.length];
                for (int i = 0; i < topk.length; i++) ret.topk[i] = topk[i];
            }
            return ret;
        }

        public String getClusterAggString() throws Exception {
            JsonObject jsonObj = new JsonObject();

            // add numeric aggs
            for (String key : numericalAggs.keySet())
                jsonObj.addProperty(key, numericalAggs.get(key));

            // turn convexhull into json array of json arrays
            JsonArray convexHullArr = new JsonArray();
            for (int i = 0; i < convexHull.length; i++) {
                JsonArray arr = new JsonArray();
                arr.add(convexHull[i][0]);
                arr.add(convexHull[i][1]);
                convexHullArr.add(arr);
            }
            jsonObj.add("convexHull", convexHullArr);

            // turn topk into an array of json objects
            JsonArray topkArr = new JsonArray();
            for (int i = 0; i < topk.length; i++) {
                JsonObject obj = new JsonObject();
                ArrayList<String> curRow = rawRows.get(topk[i]);
                for (int j = 0; j < numRawColumnsNodes; j++)
                    obj.addProperty(graph.getColumnNamesNodes().get(j), curRow.get(j));
                topkArr.add(obj);
            }
            jsonObj.add("topk", topkArr);

            return gson.toJson(jsonObj);
        }
    }

    public class SortByZ implements Comparator<RTreeData> {

        @Override
        public int compare(RTreeData o1, RTreeData o2) {

            String zCol = graph.getzCol();
            int zColId = 0;
            try {
                zColId = graph.getColumnNamesNodes().indexOf(zCol);
            } catch (Exception e) {
                return 0; // this will probably cause an exception anyways
            }
            String zOrder = graph.getzOrder();

            float v1 = parseFloat(rawRows.get(o1.rowId).get(zColId));
            float v2 = parseFloat(rawRows.get(o2.rowId).get(zColId));
            if (v1 == v2) return 0;
            if (zOrder.equals("asc")) return v1 < v2 ? -1 : 1;
            else return v1 < v2 ? 1 : -1;
        }
    }

    private static GraphInMemoryIndexer instance = null;
    // private final int objectNumLimit = 4000; // in a 1k by 1k region
    // private final int virtualViewportSize = 1000;
    private double overlappingThreshold = 1.0;
    // private final String aggKeyDelimiter = "__";
    private final Gson gson;
    private String rpKey;
    private JsonObject renderingParams;
    private String rawNodesCsv, rawEdgesCsv, projectName;
    // private String[] rawColumnsNodes, rawColumnsEdges;
    private int graphIndex, numLevels;
    private Statement bboxStmt, rawDbStmt;

    // One Rtree per level to store clusters
    // https://github.com/davidmoten/rtree
    // private RTree<RTreeData, Rectangle> rtree0, rtree1;
    private ArrayList<ArrayList<String>> rawRows;
    private List<String[]> rawNodes, rawEdges;
    private String[] rawNodesTitles, rawEdgesTitles;
    private int numRawColumnsNodes, numRawColumnsEdges;
    private Graph graph;    

    // singleton pattern to ensure only one instance existed
    private GraphInMemoryIndexer() {
        gson = new GsonBuilder().create();
    }

    // thread-safe instance getter
    public static synchronized GraphInMemoryIndexer getInstance() {

        if (instance == null) instance = new GraphInMemoryIndexer();
        return instance;
    }

    private void loadRawData(String nodesCsvFile, String edgesCsvFile) throws FileNotFoundException, IOException {
        this.rawNodesCsv = nodesCsvFile;
        this.rawEdgesCsv = edgesCsvFile;
        System.out.println("cwd: " + System.getProperty("user.dir"));
        // user.dir is /kyrix/back-end
        // System.out.println("raw data files set to: " + this.rawNodesCsv + " " + this.rawEdgesCsv);

        // try {
        //     CSVReader reader = new CSVReader(new FileReader(this.rawNodesCsv));
        //     this.rawColumnsNodes = reader.readNext();
        //     this.numRawColumnsNodes = this.rawColumnsNodes.length;

        //     reader = new CSVReader(new FileReader(this.rawEdgesCsv));
        //     this.rawColumnsEdges = reader.readNext();
        //     this.numRawColumnsEdges = this.rawColumnsEdges.length;
        // }
        // catch (Exception e) {
        //     System.out.println(e.getMessage());
        // }
    }

    @Override
    public void createMV(Canvas c, int layerId) throws Exception {

        // create MV for all graph canvases at once
        String canvasId = c.getId();
        int cId = Integer.valueOf(canvasId.substring(canvasId.indexOf("_level") + 6));
        if (cId > 0) return;    // since we are creating MV for all graph canvases at once,
        String curGraphId = c.getLayers().get(layerId).getGraphId();
        if (!curGraphId.contains("node"))
            // we create MV only for the nodes layers
            // clustering need not be performed again for edges layers
            return;

        rpKey = "graph_" + curGraphId.substring(0, curGraphId.indexOf("_"));
        System.out.println(rpKey);
        renderingParams = new JsonParser().parse(Main.getProject().getRenderingParams()).getAsJsonObject().get(rpKey).getAsJsonObject();
        graphIndex = Integer.valueOf(curGraphId.substring(0, curGraphId.indexOf("_")));

        // set common variables
        setCommonVariables();

        // compute layout
        System.out.println("Computing Layout...");
        long st = System.nanoTime();
        computeLayout();
        System.out.println("Computing layout took " + (System.nanoTime() - st) / 1e9 + "s.");

        // compute cluster aggregations
        // System.out.println("Computing Clusters...");
        st = System.nanoTime();
        computeClusterAggs();
        // System.out.println("Computing Clustering took " + (System.nanoTime() - st) / 1e9 + "s.");

        // clean up
        cleanUp();
    }


    private void computeLayout() throws Exception {
        String s;
        Process p;

        String algorithm = graph.getLayoutAlgorithm();
        ArrayList<Float> params = graph.getLayoutParams();
        String layoutAlgorithmParams;

        if (algorithm.equals("openORD")) {
            float maxLevel = params.get(0);
            float startLevel = params.get(1);
            float lastCut = params.get(2);
            float refineCut = params.get(3);
            float finalCut = params.get(4);
            layoutAlgorithmParams = "" + maxLevel + "," + startLevel + "," + lastCut + "," +  refineCut + "," + finalCut + " ";
            System.out.println("Running OpenORD layout algorithm with params: maxLevel=" + maxLevel + ", startLevel=" + startLevel + ", lastCut=" + lastCut + ", refineCut=" + refineCut + ", finalCut=" + finalCut);
            System.out.println("layoutAlgoParams: " + layoutAlgorithmParams);
        }
        else if (algorithm.equals("fm3")) {
            float param1 = params.get(0);
            float param2 = params.get(1);
            float param3 = params.get(2);
            layoutAlgorithmParams = "[" + param1 + "," + param2 + "," + param3 +"] ";
            System.out.println("Running FM3 layout algorithm with params: param1=" + param1 + ", param2=" + param2 + ", param3=" + param3);
        }
        else {
            // algorithm.equals("fa2")
            float param1 = params.get(0);
            float param2 = params.get(1);
            float param3 = params.get(2);
            layoutAlgorithmParams = "[" + param1 + "," + param2 + "," + param3 +"] ";
            System.out.println("Running ForceAtlas2 layout algorithm with params: param1=" + param1 + ", param2=" + param2 + ", param3=" + param3);
        }

        String generalParams = "--projectName " + projectName + " --nodes " + rawNodesCsv + " --edges " + rawEdgesCsv + " --algorithm " + algorithm + " ";
        
        String layout = "./layout.sh " + generalParams + "--layoutParams " + layoutAlgorithmParams;
        
        System.out.println("layout call: " + layout);

        String[] layoutCall = {"sh", "-c", layout};
        
        try {
            p = Runtime.getRuntime().exec(layoutCall, null, new File("src/main/wrappers"));

            BufferedReader br = new BufferedReader(
                new InputStreamReader(p.getInputStream()));
            while ((s = br.readLine()) != null)
                System.out.println("layout step: " + s);
            p.waitFor();
            System.out.println ("exit: " + p.exitValue());
            if (p.exitValue() == 0) {
                System.out.println("layout computed without errors...");
            }
            p.destroy();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

    }

    private void computeClustering(ArrayList<Integer> clusterLevels) throws Exception {
        Process p;

        String clusteringAlgorithm = graph.getClusteringAlgorithm();
        String layoutAlgorithm = graph.getLayoutAlgorithm();
        ArrayList<Float> params = graph.getClusteringParams();
        String clusteringAlgorithmParams = "";

        String aggMeasuresNodesFields = "";
        String aggMeasuresNodesFunctions = "";
        String aggMeasuresEdgesFields = "";
        String aggMeasuresEdgesFunctions = "";

        if (graph.getClusterAggMeasuresNodesFields() != null) {
            for (String s : graph.getClusterAggMeasuresNodesFields()) {
                aggMeasuresNodesFields += s + ",";
            }
            aggMeasuresNodesFields = aggMeasuresNodesFields.substring(0, aggMeasuresNodesFields.length()-1);
        }

        if (graph.getClusterAggMeasuresNodesFunctions() != null) {
            for (String s : graph.getClusterAggMeasuresNodesFunctions()) {
                aggMeasuresNodesFunctions += s + ",";
            }
            aggMeasuresNodesFunctions = aggMeasuresNodesFunctions.substring(0, aggMeasuresNodesFunctions.length()-1);
        }

        if (graph.getClusterAggMeasuresEdgesFields() != null) {
            for (String s : graph.getClusterAggMeasuresEdgesFields()) {
                aggMeasuresEdgesFields += s + ",";
            }
            aggMeasuresEdgesFields = aggMeasuresEdgesFields.substring(0, aggMeasuresEdgesFields.length()-1);
        }

        if (graph.getClusterAggMeasuresEdgesFunctions() != null) {
            for (String s : graph.getClusterAggMeasuresEdgesFunctions()) {
                aggMeasuresEdgesFunctions += s + ",";
            }
            aggMeasuresEdgesFunctions = aggMeasuresEdgesFunctions.substring(0, aggMeasuresEdgesFunctions.length()-1);
        }

        if (clusteringAlgorithm.equals("kmeans")) {
            float param1 = 0;//params.get(0);
            // float param2 = params.get(1);
            // float param3 = params.get(2);
            clusteringAlgorithmParams += param1;// + "," + param2 + "," + param3;
            System.out.println("Running kmeans clustering algorithm with params: ...");
        }
        else if (clusteringAlgorithm.equals("spectral")) {
            float param1 = params.get(0);
            float param2 = params.get(1);
            float param3 = params.get(2);
            clusteringAlgorithmParams += "[" + param1 + "," + param2 + "," + param3 +"] ";
            System.out.println("Running spectral clustering algorithm with params: param1=" + param1 + ", param2=" + param2 + ", param3=" + param3);
        }
        else {
            // algorithm.equals("fa2")
            float param1 = params.get(0);
            float param2 = params.get(1);
            float param3 = params.get(2);
            clusteringAlgorithmParams += "[" + param1 + "," + param2 + "," + param3 +"] ";
            System.out.println("Running ______ algorithm with params: param1=" + param1 + ", param2=" + param2 + ", param3=" + param3);
        }

        // get clustering levels from input clusterLevels
        String clusteringLevels = "";
        for (int i : clusterLevels) {
            clusteringLevels += String.valueOf(i) + ",";
        }
        clusteringLevels = clusteringLevels.substring(0, clusteringLevels.length()-1); //get rid of last comma

        // set general parameters for clusteringWrapper
        String generalParams = " --projectName " + projectName + " --nodes " + rawNodesCsv + " --edges " + rawEdgesCsv;
        generalParams += " --layoutAlgorithm " + layoutAlgorithm + " --clusterAlgorithm " + clusteringAlgorithm;
        generalParams += " --clusterLevels " + clusteringLevels + " --clusterParams " + clusteringAlgorithmParams;
        if (aggMeasuresNodesFields.length() > 0)
            generalParams += " --aggMeasuresNodesFields " + aggMeasuresNodesFields;
        
        if (aggMeasuresNodesFunctions.length() > 0)
            generalParams += " --aggMeasuresNodesFunctions " + aggMeasuresNodesFunctions;

        if (aggMeasuresEdgesFields.length() > 0)
            generalParams += " --aggMeasuresEdgesFields " + aggMeasuresEdgesFields;

        if (aggMeasuresEdgesFunctions.length() > 0)
            generalParams += " --aggMeasuresEdgesFunctions " + aggMeasuresEdgesFunctions;

        if (graph.isDirectedGraph())
            generalParams += " --directed " + "1";
        else
            generalParams += " --directed " + "0";

        String fields = "";
        if (renderingParams.has("nodesHover")) {
            JsonObject nodesHoverParams = renderingParams.get("nodesHover").getAsJsonObject();
            String topk = nodesHoverParams.get("topk").getAsString();
            JsonArray jsonFields = nodesHoverParams.get("hoverTableFields").getAsJsonArray();
            String orderBy = nodesHoverParams.get("orderBy").getAsString();
            String order = nodesHoverParams.get("order").getAsString();

            generalParams += " --rankListNodesTopK " + topk;
            for (JsonElement field : jsonFields)
                fields += field.getAsString() + ",";
            fields = fields.substring(0, fields.length()-1);
            generalParams += " --rankListNodesFields " + fields;
            generalParams += " --rankListNodesOrderBy " + orderBy;
            generalParams += " --rankListNodesOrder " + order;
        }
        if (renderingParams.has("edgesHover")) {
            JsonObject edgesHoverParams = renderingParams.get("edgesHover").getAsJsonObject();
            String topk = edgesHoverParams.get("topk").getAsString();
            JsonArray jsonFields = edgesHoverParams.get("hoverTableFields").getAsJsonArray();
            String orderBy = edgesHoverParams.get("orderBy").getAsString();
            String order = edgesHoverParams.get("order").getAsString();

            generalParams += " --rankListEdgesTopK " + topk;
            for (JsonElement field : jsonFields)
                fields += field.getAsString() + ",";
            fields = fields.substring(0, fields.length()-1);
            generalParams += " --rankListEdgesFields " + fields;
            generalParams += " --rankListEdgesOrderBy " + orderBy;
            generalParams += " --rankListEdgesOrder " + order;
        }
        
        String clustering = "./clustering.sh " + generalParams;
        // String clustering = "python3 clusteringWrapper.py " + generalParams;
        
        System.out.println("clustering call: " + clustering);

        String[] clusteringCall = {"sh", "-c", clustering};
        String newLine;

        try {
            p = Runtime.getRuntime().exec(clusteringCall, null, new File("src/main/wrappers"));

            BufferedReader br = new BufferedReader(
                new InputStreamReader(p.getInputStream()));
            while ((newLine = br.readLine()) != null)
                System.out.println("computing clustering: " + newLine);
            p.waitFor();
            System.out.println ("exit: " + p.exitValue());
            if (p.exitValue() == 0)
                System.out.println("clustering computed without errors");
            p.destroy();
        } catch (Exception e) {
        	System.out.println(e.getMessage());
        }

        // try {
        //     File clusterOutDir = new File("../compiler/examples/" + projectName + "/intermediary/clustering/" + clusteringAlgorithm);
        //     clusterOutDir.mkdirs();

        //     ProcessBuilder pb = new ProcessBuilder(clustering);
        //     pb.directory(new File("/kyrix/back-end/src/main/wrappers"));
        //     pb.inheritIO();
        //     p = pb.start();
            
        //     BufferedReader br = new BufferedReader(
        //         new InputStreamReader(p.getInputStream()));
        //     while ((newLine = br.readLine()) != null)
        //         System.out.println("computing clustering: " + newLine);
        //     p.waitFor();
        //     System.out.println ("exit: " + p.exitValue());
        //     p.destroy();
            
        // } catch (Exception e) {
        //     System.out.println(e.getMessage());
        // }
    }

    private void setCommonVariables() throws Exception {
        // get current Graph object
        graph = Main.getProject().getGraphs().get(graphIndex);
        
        // get current project name
        projectName = Main.getProject().getName();
        String userFilePath = "/kyrix/compiler/examples/" + projectName + "/";
        // String userFilePath = "../compiler/examples/" + projectName + "/";

        // load raw nodes and edges data
        loadRawData(userFilePath + graph.getNodesCsv(), userFilePath + graph.getEdgesCsv());
        this.numLevels = graph.getNumLevels(); 
        

        // store raw query results into memory
        // rawRows = DbConnector.getQueryResult(graph.getDb(), graph.getQueryNodes());
        // for (int i = 0; i < rawRows.size(); i++)
        //     for (int j = 0; j < numRawColumnsNodes; j++)
        //         if (rawRows.get(i).get(j) == null) rawRows.get(i).set(j, "");
        // System.out.println("Total raw nodes: " + rawRows.size() + " total node attributes: " +rawRows.get(0).size());

        // // add row number as a BGRP
        // Main.getProject().addBGRP(rpKey, "roughNodes", String.valueOf(rawRows.size()));

        // // store raw query results into memory
        // rawRows = DbConnector.getQueryResult(graph.getDb(), graph.getQueryEdges());
        // for (int i = 0; i < rawRows.size(); i++)
        //     for (int j = 0; j < numRawColumnsEdges; j++)
        //         if (rawRows.get(i).get(j) == null) rawRows.get(i).set(j, "");
        // System.out.println("Total raw edges: " + rawRows.size() + " total edge attributes: " + rawRows.get(0).size());

        // // add row number as a BGRP
        // Main.getProject().addBGRP(rpKey, "roughEdges", String.valueOf(rawRows.size()));

        // Read csv and load raw data

    }

    private void computeClusterAggs() throws Exception {

        //TODO: UNCOMMENT THIS
        ArrayList<Integer> clusterLevels = graph.getClusterLevels();
        long st = System.nanoTime();
        computeClustering(clusterLevels);
        System.out.println("Computing Clusters took " + (System.nanoTime() - st) / 1e9 + "s.");

        String clusteringAlgorithm = graph.getClusteringAlgorithm();
        String layoutAlgorithm = graph.getLayoutAlgorithm();
        String userFilePath = "/kyrix/compiler/examples/" + this.projectName + "/intermediary/clustering/";
        // all data files are created from command above, and stored as csv in /Clustering
        // now we need to read from these into DB
        st = System.nanoTime();
        for (int i = 0; i < numLevels; i++) {
            System.out.println("Loading clusters for level " + i + " ...");
            // rtree0 = RTree.star().create();
            int tempIndex = numLevels - 1 - i;
            String edgesFile = userFilePath + clusteringAlgorithm + "/" + layoutAlgorithm + "_edges_level_" + tempIndex + ".csv";
            String nodesFile = userFilePath + clusteringAlgorithm + "/" + layoutAlgorithm + "_nodes_level_" + tempIndex + ".csv";

            // an Rtree for level clusters
            // rtree1 = RTree.star().create();
            // boolean flag to determine whether we start writing to a table or not
            boolean startFlag; 

            try {
                System.out.println("writing nodes to db level " + i + "....");
                startFlag = true;
                //read nodes
                CSVReader nodesReader = new CSVReaderBuilder(new FileReader(nodesFile)).withSkipLines(0).build();
                String[] nextLine;
                List<String[]> nodes = new ArrayList<String[]>();
                int bufferCounter = 0;
                boolean overflow = false;
                
                // read from input in batches and write batches read into table to prevent overflow
                while ((nextLine = nodesReader.readNext()) != null) {
                    overflow = true;
                    nodes.add(nextLine);
                    bufferCounter++;
                    if (bufferCounter == Config.bboxBatchSize) {
                        if (startFlag == true) {
                            this.numRawColumnsNodes = nodes.get(0).length;
                            this.rawNodesTitles = nodes.remove(0);
                        }
                        this.rawNodes = nodes;
                        writeToDBNodes(i, startFlag);
                        startFlag = false;
                        bufferCounter = 0;
                        nodes.clear();
                        this.rawNodes = nodes;
                        overflow = false;
                    }
                }
                
                if (overflow) {
                    if (startFlag) {
                        this.numRawColumnsNodes = nodes.get(0).length;
                        this.rawNodesTitles = nodes.remove(0);
                    }
                    this.rawNodes = nodes;
                    writeToDBNodes(i, startFlag);
                    startFlag = false;
                    bufferCounter = 0;
                }

                writeToDBNodesEnding(i);
                
                //numRawColumnsNodes = nodes.get(0).length;
                //rawNodesTitles = nodes.remove(0);
                //rawNodes = nodes;
                
                /*
                for (int nodeidx = 0; nodeidx < nodes.size(); nodeidx++) {
                	String[] node = rawNodes.get(nodeidx);
                    RTreeData rd = new RTreeData(nodeidx);
                    rtree0 = rtree0.add(rd, Geometries.rectangle(0f, 0f, 0f, 0f));
                    //System.out.println(Arrays.toString(node));
                    double cx = new Double(node[1]);
                    double cy = new Double(node[2]);
                    float minx = (float) (cx - graph.getBboxW() * overlappingThreshold / 2);
                    float miny = (float) (cy - graph.getBboxH() * overlappingThreshold / 2);
                    float maxx = (float) (cx + graph.getBboxW() * overlappingThreshold / 2);
                    float maxy = (float) (cy + graph.getBboxH() * overlappingThreshold / 2);
                    
                    rd.minx = minx;
                    rd.miny = miny;
                    rd.maxx = maxx;
                    rd.maxy = maxy;

                    float[][] convexHullCopy = {{minx, miny}, {minx, maxy}, {maxx, maxy}, {maxx, miny}};
                    rd.convexHull = convexHullCopy;

                    RTreeData rdClone = rd.clone();
                    // scale the convex hulls
                    for (int p = 0; p < rdClone.convexHull.length; p++)
                        for (int k = 0; k < 2; k++) rdClone.convexHull[p][k] /= graph.getZoomFactor();

                    // add bbox coordinates
                    rdClone.minx = (float) minx;
                    rdClone.miny = (float) miny;
                    rdClone.maxx = (float) maxx;
                    rdClone.maxy = (float) maxy;

                    // add it to current level
                    rtree1 =
                            rtree1.add(
                                    rdClone,
                                    Geometries.rectangle(
                                            (float) minx,
                                            (float) miny,
                                            (float) maxx,
                                            (float) maxy));

                }
                */
                // assign rtree1 to rtree0
                // rtree0 = null;
                // rtree0 = rtree1;

                
                //writeToDBNodes(i, startFlag); //we do the above commented out section in here?
                System.out.println("finished writing nodes to db level "+ i + "...");


                System.out.println("writing edges to db level " + i + "....");

                startFlag = true;
                //read edges
                CSVReader edgesReader = new CSVReaderBuilder(new FileReader(edgesFile)).withSkipLines(0).build();
                List<String[]> edges = new ArrayList<String[]>();
                nextLine = null;
                bufferCounter = 0;
                overflow = false;

                while ((nextLine = edgesReader.readNext()) != null) {
                    overflow = true;
                    edges.add(nextLine);
                    bufferCounter++;
                    if (bufferCounter == Config.bboxBatchSize) {
                        if (startFlag == true) {
                            this.numRawColumnsEdges = edges.get(0).length;
                            this.rawEdgesTitles = edges.remove(0);
                        }
                        this.rawEdges = edges;
                        writeToDBEdges(i, startFlag);
                        startFlag = false;
                        bufferCounter = 0;
                        edges.clear();
                        this.rawEdges = edges;
                        overflow = false;
                    }
                }
                
                if (overflow) {
                    if (startFlag) {
                        this.numRawColumnsEdges = edges.get(0).length;
                        this.rawEdgesTitles = edges.remove(0);
                    }
                    this.rawEdges = edges;
                    writeToDBEdges(i, startFlag);
                    startFlag = false;
                    edges = null;
                    this.rawEdges = null;
                }

                writeToDBEdgesEnding(i);

                //numRawColumnsEdges = edges.get(0).length;
                //rawEdgesTitles = edges.remove(0);
                //rawEdges = edges;
                
                /*
                for (int edgeidx = 0; edgeidx < edges.size(); edgeidx++) {
                	String[] edge = rawEdges.get(edgeidx);
                    RTreeData rd = new RTreeData(edgeidx);
                    rtree0 = rtree0.add(rd, Geometries.rectangle(0f, 0f, 0f, 0f));
                    //System.out.println(Arrays.toString(node));
                    double cx = (new Double(node[1]) + new Double(node[3]))/2;
                    double cy = (new Double(node[2]) + new Double(node[4]))/2;
                    float minx = (float) (cx - graph.getBboxW() * overlappingThreshold / 2);
                    float miny = (float) (cy - graph.getBboxH() * overlappingThreshold / 2);
                    float maxx = (float) (cx + graph.getBboxW() * overlappingThreshold / 2);
                    float maxy = (float) (cy + graph.getBboxH() * overlappingThreshold / 2);
                    
                    rd.minx = minx;
                    rd.miny = miny;
                    rd.maxx = maxx;
                    rd.maxy = maxy;

                    float[][] convexHullCopy = {{minx, miny}, {minx, maxy}, {maxx, maxy}, {maxx, miny}};
                    rd.convexHull = convexHullCopy;

                    RTreeData rdClone = rd.clone();
                    // scale the convex hulls
                    for (int p = 0; p < rdClone.convexHull.length; p++)
                        for (int k = 0; k < 2; k++) rdClone.convexHull[p][k] /= graph.getZoomFactor();

                    // add bbox coordinates
                    rdClone.minx = (float) minx;
                    rdClone.miny = (float) miny;
                    rdClone.maxx = (float) maxx;
                    rdClone.maxy = (float) maxy;

                    // add it to current level
                    rtree1 =
                            rtree1.add(
                                    rdClone,
                                    Geometries.rectangle(
                                            (float) minx,
                                            (float) miny,
                                            (float) maxx,
                                            (float) maxy));

                }
                */
                // assign rtree1 to rtree0
                // rtree0 = null;
                // rtree0 = rtree1;

                
                //writeToDBEdges(i, startFlag);
                System.out.println("finished writing edges to db level " + i + "...");
                
            } catch (Exception e) {
                System.out.println(e.getMessage());
            }

        }
        System.out.println("Loading to DB and computing indexes took " + (System.nanoTime() - st) / 1e9 + "s.");

    }

    private void writeToDBNodes(int level, boolean start) throws Exception {
    	// create tables
        bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);

        // step 0: create tables for storing bboxes
        String bboxTableName = getGraphNodesBboxTableName(level);
        
        String sql;
    	
        if (start) {

            System.out.println("bboxTableName:" + bboxTableName);
            // drop table if exists
            sql = "drop table if exists " + bboxTableName + ";";
            bboxStmt.executeUpdate(sql);

            // create the bbox table
            sql = "create unlogged table " + bboxTableName + " (";
            for (int j = 0; j < this.rawNodesTitles.length; j++)
                sql += this.rawNodesTitles[j] + " text, ";
            sql += "cx double precision, cy double precision, minx double precision, miny double precision, "
                            + "maxx double precision, maxy double precision, geom box);";
            bboxStmt.executeUpdate(sql);

        }
        
        // insert clusters
        String insertSql = "insert into " + bboxTableName + " values (";
        for (int j = 0; j < this.numRawColumnsNodes + 5; j++) insertSql += "?, ";
        insertSql += "?);";

        PreparedStatement preparedStmt = DbConnector.getPreparedStatement(Config.databaseName, insertSql);
        int insertCount = 0;
        //Iterable<Entry<RTreeData, Rectangle>> clusters = rtree0.entries().toBlocking().toIterable();

        Canvas c = Main.getProject().getCanvases().get(level);
        int canvasWidth = c.getW();
        int canvasHeight = c.getH();

        for (int nodeidx = 0; nodeidx < this.rawNodes.size(); nodeidx++) {
            String[] node = this.rawNodes.get(nodeidx);
            RTreeData rd = new RTreeData(nodeidx);
            //rtree0 = rtree0.add(rd, Geometries.rectangle(0f, 0f, 0f, 0f));
            //System.out.println(Arrays.toString(node));
            double cx = new Double(node[1]) * canvasWidth;
            double cy = new Double(node[2]) * canvasHeight;
            float minx = (float) (cx - graph.getBboxW() * overlappingThreshold / 2);
            float miny = (float) (cy - graph.getBboxH() * overlappingThreshold / 2);
            float maxx = (float) (cx + graph.getBboxW() * overlappingThreshold / 2);
            float maxy = (float) (cy + graph.getBboxH() * overlappingThreshold / 2);
            
            rd.minx = minx;
            rd.miny = miny;
            rd.maxx = maxx;
            rd.maxy = maxy;

            float[][] convexHullCopy = {{minx, miny}, {minx, maxy}, {maxx, maxy}, {maxx, miny}};
            rd.convexHull = convexHullCopy;

            // scale the convex hulls
            for (int p = 0; p < rd.convexHull.length; p++)
                for (int k = 0; k < 2; k++) rd.convexHull[p][k] /= graph.getZoomFactor();


            for (int k = 0; k < this.numRawColumnsNodes; k++)
                preparedStmt.setString(k + 1, this.rawNodes.get(rd.rowId)[k].replaceAll("\'", "\'\'"));

            // preparedStmt.setString(this.numRawColumnsNodes, ""); //rd.getClusterAggString().replaceAll("\'", "\'\'"));
            
            // bounding box fields
            preparedStmt.setDouble(this.numRawColumnsNodes + 1, (minx + maxx) / 2.0);
            preparedStmt.setDouble(this.numRawColumnsNodes + 2, (miny + maxy) / 2.0);
            preparedStmt.setDouble(this.numRawColumnsNodes + 3, minx);
            preparedStmt.setDouble(this.numRawColumnsNodes + 4, miny);
            preparedStmt.setDouble(this.numRawColumnsNodes + 5, maxx);
            preparedStmt.setDouble(this.numRawColumnsNodes + 6, maxy);
            // preparedStmt.setDouble(this.numRawColumnsNodes + 7, 0);

            //System.out.println(preparedStmt);
            preparedStmt.addBatch();
            insertCount++;
            if ((insertCount + 1) % Config.bboxBatchSize == 0) preparedStmt.executeBatch();
        }

        

        /*
        for (Entry<RTreeData, Rectangle> o : clusters) {
            RTreeData rd = o.value();
            System.out.println("rowID: " + rd.rowId);

            // raw data fields
            for (int k = 0; k < rawNodesTitles.length; k++)
                preparedStmt.setString(
                        k + 1, rawNodes.get(rd.rowId)[k].replaceAll("\'", "\'\'"));

            // cluster agg
            System.out.println(preparedStmt);
            preparedStmt.setString(
                    numRawColumnsNodes + 1, "");//rd.getClusterAggString().replaceAll("\'", "\'\'"));

            // bounding box fields
            preparedStmt.setDouble(numRawColumnsNodes + 2, (rd.minx + rd.maxx) / 2.0);
            preparedStmt.setDouble(numRawColumnsNodes + 3, (rd.miny + rd.maxy) / 2.0);
            preparedStmt.setDouble(numRawColumnsNodes + 4, rd.minx);
            preparedStmt.setDouble(numRawColumnsNodes + 5, rd.miny);
            preparedStmt.setDouble(numRawColumnsNodes + 6, rd.maxx);
            preparedStmt.setDouble(numRawColumnsNodes + 7, rd.maxy);

            // batch commit
            preparedStmt.addBatch();
            insertCount++;
            if ((insertCount + 1) % Config.bboxBatchSize == 0) preparedStmt.executeBatch();
        }
        */
        
        preparedStmt.executeBatch();
        preparedStmt.close();

    }

    private void writeToDBNodesEnding(int level) throws Exception {

        // create tables
        bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);
        String bboxTableName = getGraphNodesBboxTableName(level);

        // update box
        String sql = "UPDATE " + bboxTableName + " SET geom=box( point(minx,miny), point(maxx,maxy) );";
        bboxStmt.executeUpdate(sql);

        System.out.println("creating spatial index");

        // build spatial index
        sql = "drop index if exists sp_" + bboxTableName +";";
        bboxStmt.executeUpdate(sql);

        sql = "create index sp_" + bboxTableName + " on " + bboxTableName + " using gist (geom);";
        bboxStmt.executeUpdate(sql);
        sql = "cluster " + bboxTableName + " using sp_" + bboxTableName + ";";
        bboxStmt.executeUpdate(sql);
    }

    private void writeToDBEdges(int level, boolean start) throws Exception {
        // create tables
        bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);

        // step 0: create tables for storing bboxes
        String bboxTableName = getGraphEdgesBboxTableName(level);

        String sql;

        if (start) {
            // drop table if exists
            sql = "drop table if exists " + bboxTableName + ";";
            bboxStmt.executeUpdate(sql);

            // create the bbox table
            sql = "create unlogged table " + bboxTableName + " (";
            for (int j = 0; j < this.rawEdgesTitles.length; j++)
                sql += this.rawEdgesTitles[j] + " text, ";
            // sql += "clusterAgg text, cx double precision, cy double precision, minx double precision, miny double precision, "
                        // + "maxx double precision, maxy double precision, geom box);";
            sql += "n1x double precision, n1y double precision, n2x double precision, n2y double precision, minx double precision, miny double precision, "
                            + "maxx double precision, maxy double precision, geom box);";
            bboxStmt.executeUpdate(sql);
        }

        // insert clusters
        String insertSql = "insert into " + bboxTableName + " values (";
        for (int j = 0; j < this.numRawColumnsEdges + 7; j++) insertSql += "?, ";
        insertSql += "?);";
        PreparedStatement preparedStmt =
                DbConnector.getPreparedStatement(Config.databaseName, insertSql);
        int insertCount = 0;
        // Iterable<Entry<RTreeData, Rectangle>> clusters = rtree1.entries().toBlocking().toIterable();

        Canvas c = Main.getProject().getCanvases().get(level);
        int canvasWidth = c.getW();
        int canvasHeight = c.getH();

        for (int edgeidx = 0; edgeidx < this.rawEdges.size(); edgeidx++) {
            String[] edge = rawEdges.get(edgeidx);
            RTreeData rd = new RTreeData(edgeidx);
            //rtree0 = rtree0.add(rd, Geometries.rectangle(0f, 0f, 0f, 0f));
            //System.out.println(Arrays.toString(node));
            double n1x = new Double(edge[3]) * canvasWidth;
            double n1y = new Double(edge[4]) * canvasHeight;
            double n2x = new Double(edge[5]) * canvasWidth;
            double n2y = new Double(edge[6]) * canvasHeight;
            // double cx = (n1x + n2x)/2;
            // double cy = (n1y + n2y)/2;

            double mincx = (n1x < n2x) ? n1x : n2x;
            double maxcx = (n1x > n2x) ? n1x : n2x;
            double mincy = (n1y < n2y) ? n1y : n2y;
            double maxcy = (n1y > n2y) ? n1y : n2y;
            
            float minx = (float) (mincx - graph.getBboxW() * overlappingThreshold / 2);
            float miny = (float) (mincy - graph.getBboxH() * overlappingThreshold / 2);
            float maxx = (float) (maxcx + graph.getBboxW() * overlappingThreshold / 2);
            float maxy = (float) (maxcy + graph.getBboxH() * overlappingThreshold / 2);
            
            rd.minx = minx;
            rd.miny = miny;
            rd.maxx = maxx;
            rd.maxy = maxy;

            float[][] convexHullCopy = {{minx, miny}, {minx, maxy}, {maxx, maxy}, {maxx, miny}};
            rd.convexHull = convexHullCopy;
            // scale the convex hulls
            for (int p = 0; p < rd.convexHull.length; p++)
                for (int k = 0; k < 2; k++) rd.convexHull[p][k] /= graph.getZoomFactor();

            for (int k = 0; k < this.numRawColumnsEdges; k++)
                preparedStmt.setString(k + 1, this.rawEdges.get(rd.rowId)[k].replaceAll("\'", "\'\'"));

            // preparedStmt.setString(numRawColumnsEdges + 1, ""); //rd.getClusterAggString().replaceAll("\'", "\'\'"));
            
            
            // bounding box fields
            preparedStmt.setDouble(this.numRawColumnsEdges + 1, n1x);
            preparedStmt.setDouble(this.numRawColumnsEdges + 2, n1y);
            preparedStmt.setDouble(this.numRawColumnsEdges + 3, n2x);
            preparedStmt.setDouble(this.numRawColumnsEdges + 4, n2y);
            preparedStmt.setDouble(this.numRawColumnsEdges + 5, rd.minx);
            preparedStmt.setDouble(this.numRawColumnsEdges + 6, rd.miny);
            preparedStmt.setDouble(this.numRawColumnsEdges + 7, rd.maxx);
            preparedStmt.setDouble(this.numRawColumnsEdges + 8, rd.maxy);
            // preparedStmt.setDouble(this.numRawColumnsEdges + 9, 0);

            //System.out.println(preparedStmt);
            preparedStmt.addBatch();
            insertCount++;
            if ((insertCount + 1) % Config.bboxBatchSize == 0) preparedStmt.executeBatch();

        }

        /*
        for (Entry<RTreeData, Rectangle> o : clusters) {
            RTreeData rd = o.value();

            // raw data fields
            for (int k = 0; k < numRawColumnsEdges; k++)
                preparedStmt.setString(
                        k + 1, rawRows.get(rd.rowId).get(k).replaceAll("\'", "\'\'"));

            // cluster agg
            preparedStmt.setString(
                    numRawColumnsEdges + 1, rd.getClusterAggString().replaceAll("\'", "\'\'"));

            // bounding box fields
            preparedStmt.setDouble(numRawColumnsEdges + 2, (rd.minx + rd.maxx) / 2.0);
            preparedStmt.setDouble(numRawColumnsEdges + 3, (rd.miny + rd.maxy) / 2.0);
            preparedStmt.setDouble(numRawColumnsEdges + 4, rd.minx);
            preparedStmt.setDouble(numRawColumnsEdges + 5, rd.miny);
            preparedStmt.setDouble(numRawColumnsEdges + 6, rd.maxx);
            preparedStmt.setDouble(numRawColumnsEdges + 7, rd.maxy);

            // batch commit
            preparedStmt.addBatch();
            insertCount++;
            if ((insertCount + 1) % Config.bboxBatchSize == 0) preparedStmt.executeBatch();
        }
        */
        
        preparedStmt.executeBatch();
        preparedStmt.close();

    }

    private void writeToDBEdgesEnding(int level) throws Exception {

        // create tables
        bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);
        String bboxTableName = getGraphEdgesBboxTableName(level);

        // update box
        String sql = "UPDATE " + bboxTableName + " SET geom=box( point(minx,miny), point(maxx,maxy) );";
        bboxStmt.executeUpdate(sql);

        // build spatial index
        sql = "drop index if exists sp_" + bboxTableName +";";
        bboxStmt.executeUpdate(sql);
        
        sql = "create index sp_" + bboxTableName + " on " + bboxTableName + " using gist (geom);";
        bboxStmt.executeUpdate(sql);
        sql = "cluster " + bboxTableName + " using sp_" + bboxTableName + ";";
        bboxStmt.executeUpdate(sql);
    }

    private void calculateBGRP(RTreeData[] rds, int level) throws SQLException, ClassNotFoundException {
        // add min & max weight into rendering params
        // min/max sum/count for all measure fields
        // only for circle, heatmap & contour right now
        // no grouping needed at this point
        // if (!ssv.getClusterMode().equals("circle")
        //         && !ssv.getClusterMode().equals("contour")
        //         && !ssv.getClusterMode().equals("heatmap")) return;

        String curGraphId = String.valueOf(graphIndex) + "_" + String.valueOf(level);
        // for (int i = 0; i < graph.getAggMeasureFields().size(); i++) {
        //     String curField = graph.getAggMeasureFields().get(i);
        //     String curFunction = graph.getAggMeasureFuncs().get(i);

        //     // min
        //     float minAgg = Float.MAX_VALUE;
        //     float maxAgg = Float.MIN_VALUE;
        //     for (RTreeData rd : rds) {
        //         minAgg = Math.min(minAgg, rd.numericalAggs.get(curFunction + "(" + curField + ")"));
        //         maxAgg = Math.max(maxAgg, rd.numericalAggs.get(curFunction + "(" + curField + ")"));
        //     }

        //     Main.getProject()
        //             .addBGRP(rpKey, curGraphId + "_" + curFunction + "(" + curField + ")_min",
        //                     String.valueOf(minAgg));

        //     Main.getProject()
        //             .addBGRP(rpKey, curGraphId + "_" + curFunction + "(" + curField + ")_max",
        //                     String.valueOf(maxAgg));
        // }
    }

    private void cleanUp() throws SQLException {
        // commit & close connections
        if (rawDbStmt != null) rawDbStmt.close();
        if (bboxStmt != null) bboxStmt.close();
        DbConnector.closeConnection(graph.getDb());
        DbConnector.closeConnection(Config.databaseName);

        // release memory
        // rtree0 = null;
        // rtree1 = null;
        rawRows = null;
        graph = null;
    }

    private String getGraphNodesBboxTableName(int level) {
        Canvas c = Main.getProject().getCanvases().get(level);
        for (Layer l : c.getLayers()) {
            if (l.getGraphId().contains("node"))
                return "bbox_" +
                        Main.getProject().getName() +
                        "_" +
                        c.getId() +
                        "layer0";// + 
                        // l.getGraphId().substring(l.getGraphId().indexOf("_"));
        }

        return "";
    }

    private String getGraphEdgesBboxTableName(int level) {
        Canvas c = Main.getProject().getCanvases().get(level);
        for (Layer l : c.getLayers()) {
            if (l.getGraphId().contains("edge"))
                return "bbox_" +
                        Main.getProject().getName() +
                        "_" +
                        c.getId() +
                        "layer1";// + 
                        // l.getGraphId().substring(l.getGraphId().indexOf("_"));
        }

        return "";
    }

    private void setInitialClusterAgg(RTreeData rd) throws Exception {
        // Implement only if needed
    }

    // this function assumes that convexHull of child
    // is from one level lower than parent
    private void mergeClusterAgg(RTreeData parent, RTreeData child) throws Exception {
        // Implement only if needed
    }

    private float[][] mergeConvex(float[][] parent, float[][] child) {
        Geometry parentGeom = getGeometryFromFloatArray(parent);
        Geometry childGeom = getGeometryFromFloatArray(child);
        Geometry union = parentGeom.union(childGeom);
        return getCoordsListOfGeometry(union.convexHull());
    }

    private Geometry getGeometryFromFloatArray(float[][] coords) {
        GeometryFactory gf = new GeometryFactory();
        ArrayList<Point> points = new ArrayList<>();
        for (int i = 0; i < coords.length; i++) {
            float x = coords[i][0];
            float y = coords[i][1];
            points.add(gf.createPoint(new Coordinate(x, y)));
        }
        Geometry geom = gf.createMultiPoint(GeometryFactory.toPointArray(points));
        return geom;
    }

    private float[][] getCoordsListOfGeometry(Geometry geometry) {
        Coordinate[] coordinates = geometry.getCoordinates();
        float[][] coordsList = new float[coordinates.length][2];
        for (int i = 0; i < coordinates.length; i++) {
            coordsList[i][0] = (float) coordinates[i].x;
            coordsList[i][1] = (float) coordinates[i].y;
        }
        return coordsList;
    }

    private float parseFloat(String s) {
        NumberFormat nf = NumberFormat.getInstance(Locale.US);
        try {
            return nf.parse(s).floatValue();
        } catch (Exception e) {
            return 0;
        }
    }
}