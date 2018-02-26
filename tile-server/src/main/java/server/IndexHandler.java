package server;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import main.Config;

import javax.net.ssl.HttpsURLConnection;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStream;

/**
 * Created by wenbo on 1/2/18.
 */
public class IndexHandler implements HttpHandler {

	@Override
	public void handle(HttpExchange httpExchange) throws IOException {

		System.out.println("Serving /");

		// check if it is GET request
		if (! httpExchange.getRequestMethod().equalsIgnoreCase("GET")) {
			Server.sendResponse(httpExchange, HttpsURLConnection.HTTP_BAD_METHOD, "");
			return;
		}

		// read the frontend file and return
		FileReader fr = new FileReader(Config.frontendFile);
		BufferedReader br = new BufferedReader(fr);
		StringBuilder content = new StringBuilder(1024);
		String s;
		while((s = br.readLine())!=null)
			content.append(s + "\n");

		// send back a ok response
		Server.sendResponse(httpExchange, HttpsURLConnection.HTTP_OK, content.toString());
	}
}