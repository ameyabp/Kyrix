package index;

import com.github.davidmoten.rtree.Entry;
import com.github.davidmoten.rtree.RTree;
import com.github.davidmoten.rtree.geometry.Geometries;
import com.github.davidmoten.rtree.geometry.Rectangle;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Locale;
import main.Config;
import main.DbConnector;
import main.Main;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;
import project.Canvas;
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
                for (int j = 0; j < numRawColumns; j++)
                    obj.addProperty(graph.getColumnNames().get(j), curRow.get(j));
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
                zColId = graph.getColumnNames().indexOf(zCol);
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
    // private double overlappingThreshold = 1.0;
    // private final String aggKeyDelimiter = "__";
    private final Gson gson;
    private String rpKey;
    private int graphIndex, numLevels, numRawColumns;
    private Statement bboxStmt, rawDbStmt;

    // One Rtree per level to store clusters
    // https://github.com/davidmoten/rtree
    private RTree<RTreeData, Rectangle> rtree0, rtree1;
    private ArrayList<ArrayList<String>> rawRows;
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

    @Override
    public void createMV(Canvas c, int layerId) throws Exception {

        // create MV for all graph layers at once
        String curGraphId = c.getLayers().get(layerId).getGraphId();
        int levelId = Integer.valueOf(curGraphId.substring(curGraphId.indexOf("_") + 1));
        if (levelId > 0) return;
        graphIndex = Integer.valueOf(curGraphId.substring(0, curGraphId.indexOf("_")));
        rpKey = "graph_" + String.valueOf(graphIndex);

        // set common variables
        setCommonVariables();


        // compute layout
        System.out.println("Computing Layout...");
        computeLayout();


        // compute cluster aggregations
        long st = System.nanoTime();
        //below is commented out for now - need to uncomment some commands in the dockerfile-kyrix-alpine for the clustering script to work properly
        //computeClusterAggs();
        System.out.println("Computer ClusterAggs took " + (System.nanoTime() - st) / 1e9 + "s.");

        // clean up
        cleanUp();
    }


    private static void computeLayout() throws Exception {
        String s;
        Process p;
        try {
            p = Runtime.getRuntime().exec("sh -c ./authorship.sh", null, new File("/OpenOrd-master/examples/recursive"));

            BufferedReader br = new BufferedReader(
                new InputStreamReader(p.getInputStream()));
            while ((s = br.readLine()) != null)
                System.out.println("line: " + s);
            p.waitFor();
            System.out.println ("exit: " + p.exitValue());
            p.destroy();
        } catch (Exception e) {
        	System.out.println(e.getMessage());
        }
    }

    private static void computeClustering() throws Exception {
        String s;
        Process p;
        try {
            p = Runtime.getRuntime().exec("sh -c python kMeansClusteringIterative.py 2", null, new File("/Clustering"));

            BufferedReader br = new BufferedReader(
                new InputStreamReader(p.getInputStream()));
            while ((s = br.readLine()) != null)
                System.out.println("line: " + s);
            p.waitFor();
            System.out.println ("exit: " + p.exitValue());
            p.destroy();
        } catch (Exception e) {
        	System.out.println(e.getMessage());
        }
    }

    private void setCommonVariables() throws Exception {
        // get current Graph object
        graph = Main.getProject().getGraphs().get(graphIndex);
        numLevels = graph.getNumLevels();
        numRawColumns = graph.getColumnNames().size();

        System.out.println("aggDimensionFields: " + graph.getAggDimensionFields());
        System.out.println("aggMeasureFields: " + graph.getAggMeasureFields());
        System.out.println("aggMeasureFuncs: " + graph.getAggMeasureFuncs());

        // calculate overlapping threshold
        // overlappingThreshold =
        //         Math.max(
        //                 0.2,
        //                 Math.sqrt(
        //                                 4
        //                                         * (virtualViewportSize + ssv.getBboxW() * 2)
        //                                         * (virtualViewportSize + ssv.getBboxH() * 2)
        //                                         / objectNumLimit
        //                                         / ssv.getBboxH()
        //                                         / ssv.getBboxW())
        //                         - 1);
        // overlappingThreshold = Math.max(overlappingThreshold, ssv.getOverlap());
        // System.out.println("Overlapping threshold: " + overlappingThreshold);

        // transform geo to screen coordinates if needed
        // if (!ssv.getGeoLatCol().isEmpty()) getGeoCoords();

        // store raw query results into memory
        rawRows = DbConnector.getQueryResult(graph.getDb(), graph.getQueryNodes());
        for (int i = 0; i < rawRows.size(); i++)
            for (int j = 0; j < numRawColumns; j++)
                if (rawRows.get(i).get(j) == null) rawRows.get(i).set(j, "");
        System.out.println("Total raw rows: " + rawRows.size());

        // add row number as a BGRP
        Main.getProject().addBGRP(rpKey, "roughNodes", String.valueOf(rawRows.size()));

        // store raw query results into memory
        rawRows = DbConnector.getQueryResult(graph.getDb(), graph.getQueryEdges());
        for (int i = 0; i < rawRows.size(); i++)
            for (int j = 0; j < numRawColumns; j++)
                if (rawRows.get(i).get(j) == null) rawRows.get(i).set(j, "");
        System.out.println("Total raw rows: " + rawRows.size());

        // add row number as a BGRP
        Main.getProject().addBGRP(rpKey, "roughEdges", String.valueOf(rawRows.size()));
    }

    private void computeClusterAggs() throws Exception {

        computeClustering();
        
        /*
        // initialize R-tree0
        rtree0 = RTree.star().create();
        for (int i = 0; i < rawRows.size(); i++) {
            RTreeData rd = new RTreeData(i);
            setInitialClusterAgg(rd);
            rtree0 = rtree0.add(rd, Geometries.rectangle(0f, 0f, 0f, 0f));
        }

        // bottom-up clustering
        for (int i = numLevels; i >= 0; i--) {
            //            Main.printUsedMemory("Memory consumed before clustering level" + i);
            System.out.println("merging level " + i + "...");

            // all clusters from this level
            Iterable<Entry<RTreeData, Rectangle>> curClustersIterable =
                    rtree0.entries().toBlocking().toIterable();
            RTreeData[] curClusters = new RTreeData[rtree0.size()];
            int idx = 0;
            for (Entry<RTreeData, Rectangle> o : curClustersIterable)
                curClusters[idx++] = o.value();

            // add BGRP
            calculateBGRP(curClusters, i);

            // write current level to db
            System.out.println("merging done. writing to db....");
            writeToDB(i - 1);
            System.out.println("finished writing to db...");

            //            Main.printUsedMemory("Memory consumed after clustering level" + i);
        }
        */
        
        

    }

    private void writeToDB(int level) throws Exception {
        // create tables
        bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);

        // step 0: create tables for storing bboxes
        String bboxTableName = getGraphBboxTableName(level);

        // drop table if exists
        String sql = "drop table if exists " + bboxTableName + ";";
        bboxStmt.executeUpdate(sql);

        // create the bbox table
        sql = "create unlogged table " + bboxTableName + " (";
        for (int j = 0; j < graph.getColumnNames().size(); j++)
            sql += graph.getColumnNames().get(j) + " text, ";
        sql +=
                "clusterAgg text, cx double precision, cy double precision, minx double precision, miny double precision, "
                        + "maxx double precision, maxy double precision, geom box);";
        bboxStmt.executeUpdate(sql);

        // insert clusters
        String insertSql = "insert into " + bboxTableName + " values (";
        for (int j = 0; j < numRawColumns + 6; j++) insertSql += "?, ";
        insertSql += "?);";
        PreparedStatement preparedStmt =
                DbConnector.getPreparedStatement(Config.databaseName, insertSql);
        int insertCount = 0;
        Iterable<Entry<RTreeData, Rectangle>> clusters = rtree1.entries().toBlocking().toIterable();
        for (Entry<RTreeData, Rectangle> o : clusters) {
            RTreeData rd = o.value();

            // raw data fields
            for (int k = 0; k < numRawColumns; k++)
                preparedStmt.setString(
                        k + 1, rawRows.get(rd.rowId).get(k).replaceAll("\'", "\'\'"));

            // cluster agg
            preparedStmt.setString(
                    numRawColumns + 1, rd.getClusterAggString().replaceAll("\'", "\'\'"));

            // bounding box fields
            preparedStmt.setDouble(numRawColumns + 2, (rd.minx + rd.maxx) / 2.0);
            preparedStmt.setDouble(numRawColumns + 3, (rd.miny + rd.maxy) / 2.0);
            preparedStmt.setDouble(numRawColumns + 4, rd.minx);
            preparedStmt.setDouble(numRawColumns + 5, rd.miny);
            preparedStmt.setDouble(numRawColumns + 6, rd.maxx);
            preparedStmt.setDouble(numRawColumns + 7, rd.maxy);

            // batch commit
            preparedStmt.addBatch();
            insertCount++;
            if ((insertCount + 1) % Config.bboxBatchSize == 0) preparedStmt.executeBatch();
        }
        preparedStmt.executeBatch();
        preparedStmt.close();

        // update box
        sql = "UPDATE " + bboxTableName + " SET geom=box( point(minx,miny), point(maxx,maxy) );";
        bboxStmt.executeUpdate(sql);

        // build spatial index
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
        for (int i = 0; i < graph.getAggMeasureFields().size(); i++) {
            String curField = graph.getAggMeasureFields().get(i);
            String curFunction = graph.getAggMeasureFuncs().get(i);

            // min
            float minAgg = Float.MAX_VALUE;
            float maxAgg = Float.MIN_VALUE;
            for (RTreeData rd : rds) {
                minAgg = Math.min(minAgg, rd.numericalAggs.get(curFunction + "(" + curField + ")"));
                maxAgg = Math.max(maxAgg, rd.numericalAggs.get(curFunction + "(" + curField + ")"));
            }

            Main.getProject()
                    .addBGRP(rpKey, curGraphId + "_" + curFunction + "(" + curField + ")_min",
                            String.valueOf(minAgg));

            Main.getProject()
                    .addBGRP(rpKey, curGraphId + "_" + curFunction + "(" + curField + ")_max",
                            String.valueOf(maxAgg));
        }
    }

    private void cleanUp() throws SQLException {
        // commit & close connections
        if (rawDbStmt != null) rawDbStmt.close();
        if (bboxStmt != null) bboxStmt.close();
        DbConnector.closeConnection(graph.getDb());
        DbConnector.closeConnection(Config.databaseName);

        // release memory
        rtree0 = null;
        rtree1 = null;
        rawRows = null;
        graph = null;
    }

    private String getGraphBboxTableName(int level) {
        String graphId = String.valueOf(graphIndex) + "_" + String.valueOf(level);
        for (Canvas c : Main.getProject().getCanvases()) {
            int numLayers = c.getLayers().size();
            for (int layerId = 0; layerId < numLayers; layerId++) {
                if (c.getLayers().get(layerId).isStatic()) continue;
                String curGraphId = c.getLayers().get(layerId).getGraphId();
                if (curGraphId == null) continue;
                if (curGraphId.equals(graphId))
                    return "bbox_"
                            + Main.getProject().getName()
                            + "_"
                            + c.getId()
                            + "layer"
                            + layerId;
            }
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