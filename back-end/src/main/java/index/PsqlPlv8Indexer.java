package index;

import box.Box;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import main.Config;
import main.DbConnector;
import main.Main;
import project.Canvas;
import project.Layer;
import project.Placement;
import project.Transform;

/** Created by wenbo on 9/30/19. */
public class PsqlPlv8Indexer extends BoundingBoxIndexer {

    private static PsqlPlv8Indexer instance = null;
    private static final int NUM_PARTITIONS = 50; // 50 partitions - for now

    private PsqlPlv8Indexer() {}

    // thread-safe instance getter
    public static synchronized PsqlPlv8Indexer getInstance() {

        if (instance == null) instance = new PsqlPlv8Indexer();
        return instance;
    }

    @Override
    public void createMV(Canvas c, int layerId) throws SQLException, ClassNotFoundException {

        Statement bboxStmt = DbConnector.getStmtByDbName(Config.databaseName);
        Layer l = c.getLayers().get(layerId);
        Transform trans = l.getTransform();

        // drop bbox table if exists
        String bboxTableName =
                "bbox_" + Main.getProject().getName() + "_" + c.getId() + "layer" + layerId;
        String sql = "drop table if exists " + bboxTableName + ";";
        System.out.println(sql);
        bboxStmt.executeUpdate(sql);

        // create bbox table
        sql = "CREATE UNLOGGED TABLE " + bboxTableName + " (";
        ArrayList<String> colNames = trans.getColumnNames();
        for (int i = 0; i < colNames.size(); i++) sql += colNames.get(i) + " text, ";
        sql +=
                "cx double precision, cy double precision, "
                        + "minx double precision, miny double precision, "
                        + "maxx double precision, maxy double precision, geom box, partition_id int) "
                        + "PARTITION BY LIST (partition_id);";
        System.out.println(sql);
        bboxStmt.executeUpdate(sql);

        // create bbox table's partitions
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            sql =
                    "CREATE UNLOGGED TABLE "
                            + bboxTableName
                            + "_"
                            + i
                            + " PARTITION OF "
                            + bboxTableName
                            + " FOR VALUES IN ("
                            + i
                            + ");";
            System.out.println(sql);
            bboxStmt.executeUpdate(sql);
        }

        // if this is an empty layer, return
        if (trans.getDb().equals("")) return;

        // check that raw data is in kyrix db
        if (!trans.getDb().equals(Config.databaseName))
            throw new IllegalArgumentException(
                    "To use the Plv8 indexer, raw data must be in the **"
                            + Config.database
                            + "** database.");

        // create trans function
        String transFuncName = bboxTableName + "_transform_func";
        bboxStmt.executeUpdate("DROP FUNCTION IF EXISTS " + transFuncName);

        // TODO: optimize the case where there is no transform func
        sql =
                "CREATE or REPLACE FUNCTION "
                        + transFuncName
                        + "(obj json, cw int, ch int, params json) RETURNS json "
                        + "AS $$ "
                        + trans.getTransformFuncBody()
                        + " $$ LANGUAGE plv8 PARALLEL SAFE";
        System.out.println(sql);
        bboxStmt.executeUpdate(sql);

        // ================= constructing the big sql =================
        sql = "INSERT INTO " + bboxTableName + "(";
        for (int i = 0; i < colNames.size(); i++) sql += colNames.get(i) + ", ";
        sql += "cx, cy, minx, miny, maxx, maxy, geom, partition_id) " + "SELECT ";

        // raw fields
        for (int i = 0; i < colNames.size(); i++) sql += colNames.get(i) + ",";

        // placement and partition_id
        if (l.isStatic()) sql += "0, 0, 0, 0, 0, 0, 0 ";
        else {
            String cx, cy, minx, miny, maxx, maxy, w, h;
            Placement p = l.getPlacement();
            cx =
                    (p.getCentroid_x().substring(0, 4).equals("full")
                            ? "0"
                            : p.getCentroid_x().substring(4));
            cy =
                    (p.getCentroid_y().substring(0, 4).equals("full")
                            ? "0"
                            : p.getCentroid_y().substring(4));
            w = (p.getWidth().substring(0, 4).equals("full") ? "1e20" : p.getWidth().substring(4));
            h =
                    (p.getHeight().substring(0, 4).equals("full")
                            ? "1e20"
                            : p.getHeight().substring(4));
            sql += cx + "::float, " + cy + "::float, ";

            // bounding box
            minx = cx + "::float - " + w + "::float / 2.0";
            miny = cy + "::float - " + h + "::float / 2.0";
            maxx = cx + "::float + " + w + "::float / 2.0";
            maxy = cy + "::float + " + h + "::float / 2.0";
            sql += minx + ", " + miny + ", " + maxx + ", " + maxy + ", ";
            sql += "box( point(" + minx + ", " + miny + "), point(" + maxx + ", " + maxy + ") ), ";

            // partition_id -- partition width into equal-sized buckets
            // requiring that c.getWsql is empty
            if (!c.getwSql().isEmpty())
                throw new IllegalArgumentException(
                        "Canvas " + c.getId() + " has non-fixed width, partition failed.");
            double partitionWidth = (double) (c.getW() + 1) / NUM_PARTITIONS;
            sql += "floor(" + cx + "::float / " + partitionWidth + ") ";
        }

        // run trans func
        sql += "FROM (SELECT ";
        for (int i = 0; i < colNames.size(); i++)
            sql +=
                    "(v->>'"
                            + colNames.get(i)
                            + "') as "
                            + colNames.get(i)
                            + (i < colNames.size() - 1 ? ", " : " ");
        sql +=
                "FROM ("
                        + "SELECT "
                        + transFuncName
                        + "(row_to_json(rawquery),"
                        + c.getW()
                        + ","
                        + c.getH()
                        + ",\'"
                        + Main.getProject().getRenderingParams().replaceAll("\'", "\'\'")
                        + "\'::json) v FROM ("
                        + removeTrailingSemiColon(trans.getQuery())
                        + ") rawquery"
                        + ") transjson"
                        + ") transsql";
        System.out.println(sql);
        long st = System.currentTimeMillis();
        bboxStmt.executeUpdate(sql);
        System.out.println(
                "Running transform func took: "
                        + (System.currentTimeMillis() - st) / 1000.0
                        + "s.");

        // create spatial index
        sql = "CREATE INDEX sp_" + bboxTableName + " ON " + bboxTableName + " USING gist (geom);";
        System.out.println(sql);
        st = System.currentTimeMillis();
        bboxStmt.executeUpdate(sql);
        System.out.println(
                "Creating spatial indexes took: "
                        + (System.currentTimeMillis() - st) / 1000.0
                        + "s.");

        // CLUSTER
        st = System.currentTimeMillis();
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            sql =
                    "CLUSTER "
                            + bboxTableName
                            + "_"
                            + i
                            + " USING "
                            + bboxTableName
                            + "_"
                            + i
                            + "_geom_idx;";
            System.out.println(sql);
            long stt = System.currentTimeMillis();
            bboxStmt.executeUpdate(sql);
            System.out.println(
                    "CLUSTERing Partition #"
                            + i
                            + " took "
                            + (System.currentTimeMillis() - stt) / 1000.0
                            + "s.");
        }
        System.out.println(
                "CLUSTERing in total took: " + (System.currentTimeMillis() - st) / 1000.0 + "s.");
        bboxStmt.close();
    }

    public String removeTrailingSemiColon(String q) {
        while (q.charAt(q.length() - 1) == ' ') q = q.substring(0, q.length() - 1);
        if (q.charAt(q.length() - 1) == ';') q = q.substring(0, q.length() - 1);
        return q;
    }

    @Override
    public ArrayList<ArrayList<String>> getDataFromRegion(
            Canvas c, int layerId, String regionWKT, String predicate, Box newBox, Box oldBox)
            throws Exception {

        // get column list string
        String colListStr = c.getLayers().get(layerId).getColStr("");

        // final data
        ArrayList<ArrayList<String>> ret = new ArrayList<>();

        // minPartitionID & maxParititonId
        double partitionWidth = (double) c.getW() / NUM_PARTITIONS;
        int minPartitionId = (int) Math.floor(newBox.getMinx() / partitionWidth);
        int maxPartitionId = (int) Math.floor(newBox.getMaxx() / partitionWidth);

        // loop through all partitions (hopefully it's one most of the time)
        for (int i = minPartitionId; i <= maxPartitionId; i++) {
            // construct range query
            String sql =
                    "select "
                            + colListStr
                            + " from bbox_"
                            + Main.getProject().getName()
                            + "_"
                            + c.getId()
                            + "layer"
                            + layerId
                            + "_"
                            + i
                            + " where ";
            sql += "geom && box('" + newBox.getCSV() + "')";
            if (oldBox.getWidth()
                    > 0) // when there is not an old box, oldBox is set to -1e5, -1e5,...
            sql += "and not (geom && box('" + oldBox.getCSV() + "') )";
            if (predicate.length() > 0) sql += " and " + predicate + ";";
            System.out.println(sql);

            // return
            ret.addAll(DbConnector.getQueryResult(Config.databaseName, sql));
        }

        return ret;
    }

    @Override
    public ArrayList<ArrayList<String>> getDataFromTile(
            Canvas c, int layerId, int minx, int miny, String predicate) throws Exception {
        return null;
    }
}
