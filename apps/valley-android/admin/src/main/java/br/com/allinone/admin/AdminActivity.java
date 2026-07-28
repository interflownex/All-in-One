package br.com.allinone.admin;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public final class AdminActivity extends Activity {
    private static final String ADMIN_HOST = "9135635066da434181.v2.appdeploy.ai";
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(7, 10, 23));
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            settings.setSafeBrowsingEnabled(true);
        }

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptThirdPartyCookies(webView, false);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return openExternalWhenNeeded(request.getUrl());
            }

            @Override
            public void onReceivedError(
                WebView view,
                WebResourceRequest request,
                WebResourceError error
            ) {
                if (request.isForMainFrame()) {
                    showConnectionError();
                }
            }
        });

        setContentView(webView);
        if (savedInstanceState == null) {
            webView.loadUrl(BuildConfig.ADMIN_URL);
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private boolean openExternalWhenNeeded(Uri uri) {
        if ("https".equalsIgnoreCase(uri.getScheme()) && ADMIN_HOST.equalsIgnoreCase(uri.getHost())) {
            return false;
        }
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (ActivityNotFoundException ignored) {
            // Sem aplicativo compatível. A navegação permanece no painel.
        }
        return true;
    }

    private void showConnectionError() {
        String html = "<!doctype html><html lang='pt-BR'><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
            + "<style>body{margin:0;background:#070a17;color:#e2e8f0;font-family:sans-serif;display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box}"
            + ".box{max-width:520px;border:1px solid #25304d;border-radius:24px;padding:28px;background:#0b1024;text-align:center}"
            + "button{border:0;border-radius:14px;padding:13px 20px;background:#2563eb;color:white;font-weight:700}</style></head>"
            + "<body><div class='box'><h1>Painel temporariamente indisponível</h1><p>Verifique a conexão com a internet e tente novamente.</p>"
            + "<button onclick=\"location.href='" + BuildConfig.ADMIN_URL + "'\">Tentar novamente</button></div></body></html>";
        webView.loadDataWithBaseURL(BuildConfig.ADMIN_URL, html, "text/html", "utf-8", null);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.clearHistory();
            webView.removeAllViews();
            webView.destroy();
        }
        super.onDestroy();
    }
}
