package br.com.allinone.admin;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.text.TextUtils;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.activity.ComponentActivity;
import androidx.activity.OnBackPressedCallback;

public final class AdminActivity extends ComponentActivity {
    private WebView webView;
    private AdminUrlPolicy adminUrlPolicy;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        adminUrlPolicy = AdminUrlPolicy.from(BuildConfig.ADMIN_URL);
        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(7, 17, 31));
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

        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (webView != null && webView.canGoBack()) {
                    webView.goBack();
                    return;
                }
                setEnabled(false);
                getOnBackPressedDispatcher().onBackPressed();
            }
        });

        setContentView(webView);
        if (savedInstanceState == null) {
            webView.loadUrl(adminUrlPolicy.baseUrl());
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private boolean openExternalWhenNeeded(Uri uri) {
        if (adminUrlPolicy.isInternal(uri.toString())) {
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
        String safeAdminUrl = TextUtils.htmlEncode(adminUrlPolicy.baseUrl());
        String html = "<!doctype html><html lang='pt-BR'><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
            + "<style>body{margin:0;background:#07111f;color:#f7fbff;font-family:sans-serif;display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box}"
            + ".box{max-width:520px;border:1px solid #21364e;border-radius:22px;padding:28px;background:#0c1929;text-align:center}"
            + "a{display:inline-block;text-decoration:none;border-radius:12px;padding:13px 20px;background:#39d98a;color:#03140d;font-weight:700}</style></head>"
            + "<body><div class='box'><h1>Painel temporariamente indisponível</h1><p>Verifique a conexão com a internet e tente novamente.</p>"
            + "<a href='" + safeAdminUrl + "'>Tentar novamente</a></div></body></html>";
        webView.loadDataWithBaseURL(adminUrlPolicy.baseUrl(), html, "text/html", "utf-8", null);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
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
