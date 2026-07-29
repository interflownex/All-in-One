package br.com.allinone.admin;

import android.app.Dialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Message;
import android.text.TextUtils;
import android.view.ViewGroup;
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
    private Dialog authDialog;
    private AdminUrlPolicy adminUrlPolicy;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        adminUrlPolicy = AdminUrlPolicy.from(BuildConfig.ADMIN_URL);
        webView = createWebView(false);
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG);
        webView.setWebChromeClient(createMainChromeClient());
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
                if (authDialog != null && authDialog.isShowing()) {
                    authDialog.dismiss();
                    return;
                }
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

    private WebView createWebView(boolean oauthPopup) {
        WebView target = new WebView(this);
        target.setBackgroundColor(Color.rgb(7, 16, 29));

        WebSettings settings = target.getSettings();
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
        settings.setSupportMultipleWindows(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            settings.setSafeBrowsingEnabled(true);
        }

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(target, oauthPopup);
        return target;
    }

    private WebChromeClient createMainChromeClient() {
        return new WebChromeClient() {
            @Override
            public boolean onCreateWindow(
                WebView view,
                boolean isDialog,
                boolean isUserGesture,
                Message resultMsg
            ) {
                if (!isUserGesture) {
                    return false;
                }

                WebView popup = createWebView(true);
                popup.setWebViewClient(new WebViewClient() {
                    @Override
                    public boolean shouldOverrideUrlLoading(
                        WebView popupView,
                        WebResourceRequest request
                    ) {
                        Uri uri = request.getUrl();
                        if ("https".equalsIgnoreCase(uri.getScheme())) {
                            return false;
                        }
                        return openExternalWhenNeeded(uri);
                    }
                });
                popup.setWebChromeClient(new WebChromeClient() {
                    @Override
                    public void onCloseWindow(WebView window) {
                        closeAuthDialog(window);
                    }
                });

                authDialog = new Dialog(AdminActivity.this);
                authDialog.setContentView(
                    popup,
                    new ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                    )
                );
                authDialog.setOnDismissListener(ignored -> popup.destroy());
                authDialog.show();

                WebView.WebViewTransport transport =
                    (WebView.WebViewTransport) resultMsg.obj;
                transport.setWebView(popup);
                resultMsg.sendToTarget();
                return true;
            }

            @Override
            public void onCloseWindow(WebView window) {
                if (window != webView) {
                    closeAuthDialog(window);
                }
            }
        };
    }

    private void closeAuthDialog(WebView popup) {
        if (authDialog != null) {
            authDialog.dismiss();
            authDialog = null;
        }
        if (popup != null) {
            popup.stopLoading();
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
            + "<style>body{margin:0;background:#07101d;color:#f7fbff;font-family:sans-serif;display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box}"
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
        if (authDialog != null) {
            authDialog.dismiss();
            authDialog = null;
        }
        if (webView != null) {
            webView.stopLoading();
            webView.clearHistory();
            webView.removeAllViews();
            webView.destroy();
        }
        super.onDestroy();
    }
}
