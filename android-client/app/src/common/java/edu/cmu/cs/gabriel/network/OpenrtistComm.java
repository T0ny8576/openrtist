package edu.cmu.cs.gabriel.network;

import android.app.Application;
import android.util.Log;
import android.widget.ImageView;

import com.google.protobuf.ByteString;

import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.function.Consumer;
import java.util.function.Supplier;

import edu.cmu.cs.gabriel.Const;
import edu.cmu.cs.gabriel.client.results.SendSupplierResult;
import edu.cmu.cs.openrtist.GabrielClientActivity;
import edu.cmu.cs.gabriel.client.comm.ServerComm;
import edu.cmu.cs.gabriel.protocol.Protos.InputFrame;
import edu.cmu.cs.gabriel.protocol.Protos.ResultWrapper;

public class OpenrtistComm {
    private final ServerComm serverComm;
    private final ErrorConsumer onDisconnect;
    private int inputFrameCount = 0;

    public static OpenrtistComm createOpenrtistComm(
            String endpoint, int port, GabrielClientActivity gabrielClientActivity,
            ImageView referenceView, Consumer<ByteString> imageView, String tokenLimit) {
        Consumer<ResultWrapper> consumer = new ResultConsumer(
                referenceView, imageView, gabrielClientActivity);
        ErrorConsumer onDisconnect = new ErrorConsumer(gabrielClientActivity);
        ServerComm serverComm;
        Application application = gabrielClientActivity.getApplication();
        if (tokenLimit.equals("None")) {
            serverComm = ServerComm.createServerComm(
                    consumer, endpoint, port, application, onDisconnect);
        } else {
            serverComm = ServerComm.createServerComm(
                    consumer, endpoint, port, application, onDisconnect,
                    Integer.parseInt(tokenLimit));
        }

        return new OpenrtistComm(serverComm, onDisconnect);
    }

    OpenrtistComm(ServerComm serverComm, ErrorConsumer onDisconnect) {
        this.serverComm = serverComm;
        this.onDisconnect = onDisconnect;
    }

    public void sendSupplier(Supplier<InputFrame> supplier, String frameLogString, GabrielClientActivity gabrielClientActivity) {
        if (!this.serverComm.isRunning()) {
            return;
        }
        if (inputFrameCount > 500) {
            Log.w("PROFILE1", "Done 500.\n");
            return;
        }
        SendSupplierResult result = this.serverComm.sendSupplier(supplier, Const.SOURCE_NAME, /* wait */ false);
        if (result == SendSupplierResult.SUCCESS) {
            inputFrameCount++;
            String frameSentString = inputFrameCount + frameLogString + inputFrameCount + "\tClient Send\t" +
                    gabrielClientActivity.getNetworkTimeString() + "\n";
            gabrielClientActivity.logList.add(frameSentString);
        } else {
            gabrielClientActivity.logList.add("Failed to sendSupplier: frame " + (inputFrameCount + 1) + " at" + frameLogString);
        }
    }

    public void stop() {
        this.serverComm.stop();
    }
}
