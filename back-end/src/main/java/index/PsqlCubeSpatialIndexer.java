package index;

import jdk.nashorn.api.scripting.NashornScriptEngine;
import main.Config;
import main.DbConnector;
import main.Main;
import project.Canvas;
import project.Layer;
import project.Transform;
import project.Project;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.sql.SQLException;

public class PsqlCubeSpatialIndexer extends Indexer {

    private static PsqlCubeSpatialIndexer instance = null;

    private List<Integer> rowsFetched;

    private PsqlCubeSpatialIndexer() {
        rowsFetched = new ArrayList<>();
    }

    public static synchronized PsqlCubeSpatialIndexer getInstance() {
        if (instance == null)
            instance = new PsqlCubeSpatialIndexer();
        return instance;
    }

    protected void debug(String msg) {
        System.out.println("[DEBUG]:  " + msg);
    }

    @Override
    public void createMV(Canvas c, int layerId) throws Exception {
        Statement bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);
        Connection dbConn = DbConnector.getDbConn(Config.dbServer, Config.databaseName, Config.userName, Config.password);

        Layer l = c.getLayers().get(layerId);
        Transform trans = l.getTransform();
        ArrayList colNames = trans.getColumnNames();

        // step 0: create tables for storing bboxes and tiles
        // put all canvases and layers in same table
        String bboxTableName = "bbox_" + Main.getProject().getName();

        // create extension if it doesn't exist
        String extSql = "create extension if not exists cube;";
        bboxStmt.executeUpdate(extSql);

        // drop table if exists -- NO DON'T WANT TO DROP TABLE NOW ONE BIG TABLE
        // String sql = "drop table if exists " + bboxTableName + ";";
        // bboxStmt.executeUpdate(sql);

        // create the bbox table
        String sql = "create table if not exists " + bboxTableName + " (";
        for (int i = 0; i < colNames.size(); i++) {
            sql += colNames.get(i) + " text, ";
        }

        // need to add value based on canvas id and layer id
        sql += "cx double precision, cy double precision, minx double precision, miny double precision, maxx double precision, maxy double precision, v cube);";
        bboxStmt.executeUpdate(sql);

        // if this is an empty layer, return
        if (trans.getDb().equals(""))
            return ;

        // step 1: set up nashorn environment -- what is nashorn??
        NashornScriptEngine engine = null;
        if (! trans.getTransformFunc().equals(""))
            engine = setupNashorn(trans.getTransformFunc());

        // step 2: looping through query results
        // what's difference btwn separable and non-separable cases?
        Statement rawDBStmt = DbConnector.getStmtByDbName(trans.getDb());
        ResultSet rs = DbConnector.getQueryResultIterator(rawDBStmt, trans.getQuery());
        int numColumn = rs.getMetaData().getColumnCount();
        int rowCount = 0;
        String insertSql = "insert into " + bboxTableName + " values (";
        // where does the 6 come from?
        for (int i = 0; i < colNames.size() + 6; i ++) {
            insertSql += "?, ";
        }
        insertSql += "?::cube);";
        PreparedStatement preparedStmt = dbConn.prepareStatement(insertSql);
        while (rs.next()) {

            // count log
            rowCount ++;
            if (rowCount % 1000000 == 0)
                System.out.println(rowCount);

            // get raw row
            ArrayList<String> curRawRow = new ArrayList<>();
            for (int i = 1; i <= numColumn; i ++)
                curRawRow.add(rs.getString(i));

            // step 3: run transform function on this tuple
            ArrayList<String> transformedRow;
            if (! trans.getTransformFunc().equals(""))
                transformedRow = getTransformedRow(c, curRawRow, engine);
            else
                transformedRow = curRawRow;

            // step 4: calculate bounding boxes
            ArrayList<Double> curBbox = getBboxCoordinates(l, transformedRow);

            // insert into bbox table
            for (int i = 0; i < transformedRow.size(); i ++)
                // preparedStmt.setString(i + 1, transformedRow.get(i).replaceAll("\'", "\'\'"));
                preparedStmt.setString(i + 1, transformedRow.get(i));
            for (int i = 0; i < 6; i ++)
                preparedStmt.setDouble(transformedRow.size() + i + 1, curBbox.get(i));

            double minx, miny, maxx, maxy;
            minx = curBbox.get(2);
            miny = curBbox.get(3);
            maxx = curBbox.get(4);
            maxy = curBbox.get(5);
            
            preparedStmt.setString(transformedRow.size() + 7,
                    // getPolygonText(minx, miny, maxx, maxy));
                    getCubeText(minx, miny, maxx, maxy, c.getId()));
            preparedStmt.addBatch();

            if (rowCount % Config.bboxBatchSize == 0) {
                preparedStmt.executeBatch();
            }
        }
        rs.close();
        rawDBStmt.close();
        DbConnector.closeConnection(trans.getDb());

        // insert tail stuff
        if (rowCount % Config.bboxBatchSize != 0) {
            preparedStmt.executeBatch();
        }
        preparedStmt.close();

        // index on inserted data if the canvas is the bottom-most canvas
        Project proj = Main.getProject();
        ArrayList<Canvas> canvases = proj.getCanvases();
        Canvas bottomCanvas = canvases.get(canvases.size() - 1);
        if (c.getId() == bottomCanvas.getId())
            /*
            sql:
                create index idx_tbl_cube_1 on tbl_cube using gist (v);
            */
            sql = "create index cube_idx_" + bboxTableName + " on " + bboxTableName + " using gist (v);";
            bboxStmt.executeUpdate(sql);
        
        bboxStmt.close();
    }

    @Override
    public ArrayList<ArrayList<String>> getDataFromRegion(Canvas c, int layerId, String regionWKT, String predicate)
            throws Exception {
        
        // get column list string
        String colListStr = c.getLayers().get(layerId).getTransform().getColStr("");


        System.out.println("in psql cube spatial indexer");
        // construct range query
        String sql = "select " + colListStr + " from bbox_" + Main.getProject().getName()
                + " where v && ";
        sql += regionWKT;
        if (predicate.length() > 0) 
            sql += " and " + predicate + ";";
        else
            sql += ";";
        System.out.println(sql);

        
        ArrayList<ArrayList<String>> queryResult = DbConnector.getQueryResult(Config.databaseName, sql);
        

        return queryResult;
    }

    @Override
    public ArrayList<ArrayList<String>> getDataFromTile(Canvas c, int layerId, int minx, int miny, String predicate)
            throws Exception {

        // get column list string
        String colListStr = c.getLayers().get(layerId).getTransform().getColStr("");
        Project proj = Main.getProject();
        int canvasNumId = proj.getCanvasNumId(c.getId());
        
        // make bounding box cube to intersect with
        String tileCube = "cube (" + 
            "(" + minx + ", " + miny + ", " + canvasNumId + "), " +
            "(" + (minx + Config.tileW) + ", " + (miny + Config.tileH) + ", " + canvasNumId + "))";
        
        // construct range query
        String sql = "select " + colListStr + " from bbox_" + Main.getProject().getName()
                + " where v && " + tileCube;
        
        if (predicate.length() > 0)
            sql += " and " + predicate + ";";
        else
            sql += ";";

        // return
        return DbConnector.getQueryResult(Config.databaseName, sql);
    }

    @Override
    public String getStaticDataQuery(Canvas c, Layer l, int i, ArrayList<String> predicates) {

        // get column list string
        String colListStr = l.getTransform().getColStr("");

        // construct range query
        String sql = "select " + colListStr + " from bbox_" + Config.projectName;
        if (predicates.get(i).length() > 0)
            sql += " where " + predicates.get(i);
        sql += ";";

        return sql;

    }

    private static String getCubeText(double minx, double miny, double maxx, double maxy, String canvasId) {

        String cubeText = "";
        Project proj = Main.getProject();

        /*
        sql:
        insert into tbl_cube select id, cube ( array[minx, miny, canvasid], array[minx, maxy, canvasid], array[maxx, maxy, canvasid])
        */
        
        int canvasIdNum = proj.getCanvasNumId(canvasId);
        cubeText += "(" + String.valueOf(minx) + ", " + String.valueOf(miny) + ", "
                + String.valueOf(canvasIdNum) + "), "
                + "(" + String.valueOf(maxx) + ", " + String.valueOf(maxy) + ", "
                + String.valueOf(canvasIdNum) + ")";

        return cubeText;
    }


}