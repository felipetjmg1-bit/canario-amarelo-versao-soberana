package br.com.impulsodigital.canariovpn;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.net.VpnService;
import android.os.Build;
import android.os.ParcelFileDescriptor;

public class CanarioVpnService extends VpnService {
    public static final String ACTION_START = "br.com.impulsodigital.canariovpn.START";
    public static final String ACTION_STOP = "br.com.impulsodigital.canariovpn.STOP";
    private static final String CHANNEL = "canario_vpn_status";
    private ParcelFileDescriptor tunnel;

    @Override public void onCreate() {
        super.onCreate();
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(CHANNEL, "Canário VPN", NotificationManager.IMPORTANCE_LOW);
            getSystemService(NotificationManager.class).createNotificationChannel(channel);
        }
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? ACTION_START : intent.getAction();
        if (ACTION_STOP.equals(action)) {
            closeTunnel();
            stopForeground(true);
            stopSelf();
            return START_NOT_STICKY;
        }
        Intent open = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open, PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= 23 ? PendingIntent.FLAG_IMMUTABLE : 0));
        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, CHANNEL) : new Notification.Builder(this);
        Notification notification = builder.setContentTitle("Canário VPN")
                .setContentText("Serviço iniciado • gateway VPN ainda não configurado")
                .setSmallIcon(android.R.drawable.ic_lock_lock)
                .setContentIntent(pi).setOngoing(true).build();
        startForeground(41, notification);
        // Não criamos uma rota TUN fictícia: sem endpoint/protocolo, isso bloquearia o tráfego.
        // O ponto de integração com o cliente WireGuard/OpenVPN deverá ser implementado
        // quando a Impulso Digital provisionar o gateway e as credenciais.
        return START_STICKY;
    }

    private void closeTunnel() {
        if (tunnel != null) {
            try { tunnel.close(); } catch (Exception ignored) { }
            tunnel = null;
        }
    }

    @Override public void onDestroy() {
        closeTunnel();
        super.onDestroy();
    }
}
