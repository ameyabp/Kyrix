package project;

import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import main.Config;
import main.DbConnector;

/** Created on 3/15/21. */
public class Graph {

    private String queryNodes, queryEdges, db, rawTable, nodesCsv, edgesCsv;
    private String xCol, yCol, zCol;
    private int bboxW, bboxH;
    private int topk;
    private String zOrder;
    private ArrayList<String> columnNamesNodes, queriedColumnNamesNodes = null, columnTypesNodes = null;
    private ArrayList<String> columnNamesEdges, queriedColumnNamesEdges = null, columnTypesEdges = null;
    private int topLevelWidth, topLevelHeight;
    private boolean directedGraph;
    // private double overlap;
    private double zoomFactor;
    private int xColId = -1, yColId = -1, zColId = -1;
    private String mergeClusterAggs,
            getCoordinatesFromLatLonBody,
            getCitusSpatialHashKeyBody,
            singleNodeClusteringBody,
            mergeClustersAlongSplitsBody;

    private String layoutAlgo;
    private ArrayList<Float> layoutParams;

    private String clusteringAlgo;
    private ArrayList<Float> clusteringParams;
    private ArrayList<Integer> clusterLevels;
    private int numLevels;

    private ArrayList<String> clusterAggMeasuresNodesFields;
    private ArrayList<String> clusterAggMeasuresNodesFunctions;
    private ArrayList<String> clusterAggDimensionsNodesFields;
    private ArrayList<String> clusterAggDimensionsNodesFunctions;

    private ArrayList<String> clusterAggMeasuresEdgesFields;
    private ArrayList<String> clusterAggMeasuresEdgesFunctions;
    private ArrayList<String> clusterAggDimensionsEdgesFields;
    private ArrayList<String> clusterAggDimensionsEdgesFunctions;

    public String getQueryNodes() {
        return queryNodes;
    }
    
    public String getQueryEdges() {
        return queryEdges;
    }

    public String getDb() {
        return db;
    }

    public String getxCol() {
        return xCol;
    }

    public String getyCol() {
        return yCol;
    }

    public int getBboxW() {
        return bboxW;
    }

    public int getBboxH() {
        return bboxH;
    }

    public int getTopk() {
        return topk;
    }

    public String getRawTable() {
        return rawTable;
    }

    public String getzCol() {
        return zCol;
    }

    public String getzOrder() {
        return zOrder;
    }

    public String getNodesCsv() {
        return nodesCsv;
    }

    public String getEdgesCsv() {
       return edgesCsv;
    }

    public boolean isDirectedGraph() {
        return directedGraph;
    }

    // public String getClusterMode() {
    //     return clusterMode;
    // }

    // public double getOverlap() {
    //     return overlap;
    // }

    public int getXColId() throws Exception {

        if (xColId < 0) {
            ArrayList<String> colNames = getColumnNamesNodes();
            xColId = colNames.indexOf(xCol);
        }
        return xColId;
    }

    public int getYColId() throws Exception {

        if (yColId < 0) {
            ArrayList<String> colNames = getColumnNamesNodes();
            yColId = colNames.indexOf(yCol);
        }
        return yColId;
    }

    public int getZColId() throws Exception {

        if (zColId < 0) {
            ArrayList<String> colNames = getColumnNamesNodes();
            zColId = colNames.indexOf(zCol);
        }
        return zColId;
    }

    public ArrayList<String> getColumnNamesNodes() throws Exception {

        // if it is specified already, return
        if (columnNamesNodes != null && columnNamesNodes.size() > 0) return columnNamesNodes;

        // otherwise fetch the schema from DB
        if (queriedColumnNamesNodes == null) {
            queriedColumnNamesNodes = new ArrayList<>();
            columnTypesNodes = new ArrayList<>();
            Statement rawDBStmt = DbConnector.getStmtByDbName(getDb(), true);
            String query = getQueryNodes();
            if (Config.database == Config.Database.CITUS) {
                while (query.charAt(query.length() - 1) == ';')
                    query = query.substring(0, query.length() - 1);
                // assuming there is no limit 1
                query += " LIMIT 1;";
            }
            ResultSet rs = DbConnector.getQueryResultIterator(rawDBStmt, query);
            int colCount = rs.getMetaData().getColumnCount();
            for (int i = 1; i <= colCount; i++) {
                queriedColumnNamesNodes.add(rs.getMetaData().getColumnName(i));
                columnTypesNodes.add(rs.getMetaData().getColumnTypeName(i));
            }
            rs.close();
            rawDBStmt.close();
            DbConnector.closeConnection(getDb());
        }

        return queriedColumnNamesNodes;
    }

    public ArrayList<String> getColumnTypesNodes() throws Exception {
        if (columnTypesNodes != null) return columnTypesNodes;
        getColumnNamesNodes();
        return columnTypesNodes;
    }

    public ArrayList<String> getColumnNamesEdges() throws Exception {

        // if it is specified already, return
        if (columnNamesEdges != null && columnNamesEdges.size() > 0) return columnNamesEdges;

        // otherwise fetch the schema from DB
        if (queriedColumnNamesEdges == null) {
            queriedColumnNamesEdges = new ArrayList<>();
            columnTypesEdges = new ArrayList<>();
            Statement rawDBStmt = DbConnector.getStmtByDbName(getDb(), true);
            String query = getQueryEdges();
            if (Config.database == Config.Database.CITUS) {
                while (query.charAt(query.length() - 1) == ';')
                    query = query.substring(0, query.length() - 1);
                // assuming there is no limit 1
                query += " LIMIT 1;";
            }
            ResultSet rs = DbConnector.getQueryResultIterator(rawDBStmt, query);
            int colCount = rs.getMetaData().getColumnCount();
            for (int i = 1; i <= colCount; i++) {
                queriedColumnNamesEdges.add(rs.getMetaData().getColumnName(i));
                columnTypesEdges.add(rs.getMetaData().getColumnTypeName(i));
            }
            rs.close();
            rawDBStmt.close();
            DbConnector.closeConnection(getDb());
        }

        return queriedColumnNamesEdges;
    }

    public ArrayList<String> getColumnTypesEdges() throws Exception {
        if (columnTypesEdges != null) return columnTypesEdges;
        getColumnNamesEdges();
        return columnTypesEdges;
    }

    public ArrayList<String> getClusterAggDimensionsNodesFields() {
        return clusterAggDimensionsNodesFields;
    }

    public ArrayList<String> getClusterAggDimensionsNodesFunctions() {
        return clusterAggDimensionsNodesFunctions;
    }

    public ArrayList<String> getClusterAggMeasuresNodesFields() {
        return clusterAggMeasuresNodesFields;
    }

    public ArrayList<String> getClusterAggMeasuresNodesFunctions() {
        return clusterAggMeasuresNodesFunctions;
    }
    
    public ArrayList<String> getClusterAggDimensionsEdgesFields() {
        return clusterAggDimensionsEdgesFields;
    }

    public ArrayList<String> getClusterAggDimensionsEdgesFunctions() {
        return clusterAggDimensionsEdgesFunctions;
    }

    public ArrayList<String> getClusterAggMeasuresEdgesFields() {
        return clusterAggMeasuresEdgesFields;
    }

    public ArrayList<String> getClusterAggMeasuresEdgesFunctions() {
        return clusterAggMeasuresEdgesFunctions;
    }

    public int getNumLevels() {
        return numLevels;
    }

    public int getTopLevelWidth() {
        return topLevelWidth;
    }

    public int getTopLevelHeight() {
        return topLevelHeight;
    }

    public double getZoomFactor() {
        return zoomFactor;
    }

    public String getClusteringAlgorithm() {
        return clusteringAlgo;
    }

    public ArrayList<Float> getClusteringParams() {
        return clusteringParams;
    }

    public ArrayList<Integer> getClusterLevels() {
        return clusterLevels;
    }

    public String getLayoutAlgorithm() {
        return layoutAlgo;
    }

    public ArrayList<Float> getLayoutParams() {
        return layoutParams;
    }

    // public double getLoX() {
    //     return loX;
    // }

    // public double getLoY() {
    //     return loY;
    // }

    // public double getHiX() {
    //     return hiX;
    // }

    // public double getHiY() {
    //     return hiY;
    // }

    // public double getGeoLat() {
    //     return geoLat;
    // }

    // public double getGeoLon() {
    //     return geoLon;
    // }

    // public String getGeoLatCol() {
    //     return geoLatCol;
    // }

    // public String getGeoLonCol() {
    //     return geoLonCol;
    // }

    // public int getGeoInitialLevel() {
    //     return geoInitialLevel;
    // }

    // public boolean isMapBackground() {
    //     return mapBackground;
    // }

    public String getMergeClusterAggs() {
        return mergeClusterAggs;
    }

    public String getGetCoordinatesFromLatLonBody() {
        return getCoordinatesFromLatLonBody;
    }

    public String getGetCitusSpatialHashKeyBody() {
        return getCitusSpatialHashKeyBody;
    }

    public String getSingleNodeClusteringBody() {
        return singleNodeClusteringBody;
    }

    public String getMergeClustersAlongSplitsBody() {
        return mergeClustersAlongSplitsBody;
    }

    // get the canvas coordinate of a raw value
    // public double getCanvasCoordinate(int level, double v, boolean isX) throws Exception {

    //     setXYExtent();
    //     if (isX)
    //         return ((topLevelWidth - bboxW) * (v - loX) / (hiX - loX) + bboxW / 2.0)
    //                 * Math.pow(zoomFactor, level);
    //     else
    //         return ((topLevelHeight - bboxH) * (v - loY) / (hiY - loY) + bboxH / 2.0)
    //                 * Math.pow(zoomFactor, level);
    // }

    // public void setXYExtent() throws Exception {
    //     // calculate range if have not
    //     if (Double.isNaN(loX)) {

    //         System.out.println("\n Calculating Graph x & y ranges...\n");
    //         loX = loY = Double.MAX_VALUE;
    //         hiX = hiY = Double.MIN_VALUE;
    //         Statement rawDBStmt = DbConnector.getStmtByDbName(getDb(), true);
    //         ResultSet rs = DbConnector.getQueryResultIterator(rawDBStmt, getQueryNodes());
    //         while (rs.next()) {
    //             double cx = rs.getDouble(getXColId() + 1);
    //             double cy = rs.getDouble(getYColId() + 1);
    //             loX = Math.min(loX, cx);
    //             hiX = Math.max(hiX, cx);
    //             loY = Math.min(loY, cy);
    //             hiY = Math.max(hiY, cy);
    //         }
    //         rawDBStmt.close();
    //         DbConnector.closeConnection(getDb());
    //     }
    // }

    @Override
    public String toString() {
        return "Graph{"
                + "queryNodes='"
                + queryNodes
                + '\''
                + "queryEdges='"
                + queryEdges
                + '\''
                + ", db='"
                + db
                + '\''
                + ", xCol='"
                + xCol
                + '\''
                + ", yCol='"
                + yCol
                + '\''
                + ", bboxW="
                + bboxW
                + ", bboxH="
                + bboxH
                + '\''
                + ", columnNamesNodes="
                + columnNamesNodes
                + ", columnNamesEdges="
                + columnNamesEdges
                + ", numLevels="
                + numLevels
                + ", clusterLevels="
                + clusterLevels
                + ", topLevelWidth="
                + topLevelWidth
                + ", topLevelHeight="
                + topLevelHeight
                + ", zoomFactor="
                + zoomFactor
                + '}';
    }
}
