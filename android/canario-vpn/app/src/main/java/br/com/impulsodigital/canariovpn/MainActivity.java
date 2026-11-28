package br.com.impulsodigital.canariovpn;

import android.app.Activity;
import android.content.Intent;
import android.net.VpnService;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.net.TrafficStats;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

import java.util.Locale;

public class MainActivity extends Activity {
    private final Handler handler = new Handler(Looper.getMainLooper());
    private TextView timer, status, session, download, upload, dataDown, dataUp, balance, message;
    private long seconds = 0, sessionStart = 0, lastRx = 0, lastTx = 0;
    private boolean connected = false;
    private static final int VPN_REQUEST = 701;
    private final int bg = Color.rgb(13,16,23), panel = Color.rgb(27,32,43), white = Color.WHITE;
    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            if (connected) {
                if (seconds > 0) seconds--;
                timer.setText(format(seconds));
                session.setText("Sessão: " + format((System.currentTimeMillis()-sessionStart)/1000));
                long rx = TrafficStats.getTotalRxBytes(), tx = TrafficStats.getTotalTxBytes();
                download.setText(String.format(Locale.US, "%.1f KB/s", Math.max(0,rx-lastRx)/1024.0));
                upload.setText(String.format(Locale.US, "%.1f KB/s", Math.max(0,tx-lastTx)/1024.0));
                dataDown.setText(String.format(Locale.US, "%.2f MB", rx/1048576.0));
                dataUp.setText(String.format(Locale.US, "%.2f MB", tx/1048576.0));
                lastRx=rx; lastTx=tx;
                if (seconds == 0) disconnect();
            }
            handler.postDelayed(this,1000);
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(bg); getWindow().setNavigationBarColor(bg);
        buildUi();
        handler.post(ticker);
    }

    private TextView text(String value, int size, int color) {
        TextView v = new TextView(this); v.setText(value); v.setTextSize(size); v.setTextColor(color);
        return v;
    }
    private LinearLayout column() {
        LinearLayout l = new LinearLayout(this); l.setOrientation(LinearLayout.VERTICAL); l.setPadding(18,14,18,14);
        return l;
    }
    private LinearLayout card() {
        LinearLayout l=column(); l.setBackgroundColor(panel);
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2); p.setMargins(0,8,0,8); l.setLayoutParams(p); return l;
    }
    private Button button(String label) {
        Button b=new Button(this); b.setText(label); b.setAllCaps(false); return b;
    }
    private void buildUi() {
        ScrollView scroll=new ScrollView(this); scroll.setBackgroundColor(bg);
        LinearLayout root=column(); root.setPadding(18,18,18,24); scroll.addView(root); setContentView(scroll);
        TextView brand=text("● CANÁRIO VPN",24,white); brand.setTypeface(null,Typeface.BOLD); root.addView(brand);
        TextView company=text("IMPULSO DIGITAL SOLUÇÕES EM IA",11,Color.LTGRAY); root.addView(company);
        TextView banner=text("ESPAÇO DE ANÚNCIO • SDK RECOMPENSADO A INTEGRAR",12,Color.rgb(180,190,205));
        banner.setGravity(Gravity.CENTER); banner.setPadding(8,18,8,18); banner.setBackgroundColor(panel); root.addView(banner);
        LinearLayout timeCard=card(); root.addView(timeCard);
        timeCard.addView(text("TEMPO DE CONEXÃO RESTANTE",12,Color.LTGRAY));
        timer=text("00:00:00",38,white); timer.setTypeface(null,Typeface.BOLD); timeCard.addView(timer);
        Button add=button("+ ADD • GANHAR 15 MIN"); timeCard.addView(add);
        add.setOnClickListener(v->{ seconds+=900; timer.setText(format(seconds)); message.setText("Modo de teste: +15 minutos adicionados. Nenhum anúncio real foi exibido."); });
        Button balanceButton=button("Saldo e Histórico"); timeCard.addView(balanceButton);
        balance=text("Saldo de teste: "+seconds/60+" min • histórico local",12,Color.LTGRAY); timeCard.addView(balance);
        balanceButton.setOnClickListener(v->balance.setText("Saldo: "+seconds/60+" min • Última recompensa: simulação local"));
        LinearLayout state=card(); root.addView(state);
        status=text("● DESCONECTADO",18,Color.rgb(255,190,70)); status.setTypeface(null,Typeface.BOLD); state.addView(status);
        session=text("Sessão: 00:00:00",13,Color.LTGRAY); state.addView(session);
        Button connect=button("CONECTAR / DESCONECTAR"); state.addView(connect);
        connect.setOnClickListener(v->{ if(connected) disconnect(); else requestVpn(); });
        message=text("Demonstração: gateway VPN ainda não configurado.",12,Color.LTGRAY); state.addView(message);
        LinearLayout stats=card(); root.addView(stats);
        stats.addView(text("VELOCIDADE DE REDE (dispositivo)",14,white));
        download=text("Download: 0 KB/s",14,white); upload=text("Upload: 0 KB/s",14,white);
        dataDown=text("Download: 0 MB",13,Color.LTGRAY); dataUp=text("Upload: 0 MB",13,Color.LTGRAY);
        stats.addView(download); stats.addView(upload); stats.addView(dataDown); stats.addView(dataUp);
        LinearLayout nav=card(); root.addView(nav);
        String[] items={"Ajustes","Registro (Logs)","Atualizar","Ferramentas"};
        for(String item:items){ Button b=button(item); nav.addView(b); b.setOnClickListener(v->message.setText(item+" • módulo básico de demonstração")); }
        TextView disclaimer=text("VPN REAL INDISPONÍVEL: configure um gateway e integre um protocolo seguro antes de encaminhar tráfego. Métricas atuais são do dispositivo, não do túnel.",11,Color.LTGRAY);
        disclaimer.setPadding(4,16,4,8); root.addView(disclaimer);
    }

    private void requestVpn() {
        Intent prepare=VpnService.prepare(this);
        if(prepare!=null) startActivityForResult(prepare,VPN_REQUEST);
        else startDemoService();
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request==VPN_REQUEST && result==RESULT_OK) startDemoService();
        else message.setText("Permissão VPN não concedida.");
    }
    private void startDemoService() {
        Intent i=new Intent(this,CanarioVpnService.class); i.setAction(CanarioVpnService.ACTION_START);
        if(android.os.Build.VERSION.SDK_INT>=26) startForegroundService(i); else startService(i);
        connected=true; sessionStart=System.currentTimeMillis(); lastRx=TrafficStats.getTotalRxBytes(); lastTx=TrafficStats.getTotalTxBytes();
        status.setText("● SERVIÇO ATIVO • MODO DEMO"); status.setTextColor(Color.rgb(80,210,130));
        message.setText("Serviço Android ativo. Sem gateway, não há túnel de internet.");
    }
    private void disconnect() {
        connected=false;
        Intent i=new Intent(this,CanarioVpnService.class); i.setAction(CanarioVpnService.ACTION_STOP); startService(i);
        status.setText("● DESCONECTADO"); status.setTextColor(Color.rgb(255,190,70));
        message.setText("Serviço encerrado.");
    }
    private String format(long s) {
        s=Math.max(0,s); return String.format(Locale.US,"%02d:%02d:%02d",s/3600,(s%3600)/60,s%60);
    }
    @Override protected void onDestroy(){ handler.removeCallbacks(ticker); super.onDestroy(); }
}
