import { useEffect, useMemo, useRef, useState } from "react";
import {
  MAPBOX_COLORS,
  MAPBOX_GL_JS_VERSION,
  MAPBOX_STYLE_NIGHT,
  mapboxCredentialMessage,
  resolveNavigationStyleUri,
  tokenStatus,
} from "./mapboxConfig";
import "./mapbox-navigation.css";

// Contrato de compatibilidade auditável: mapbox-gl-js/v3.25.0
export type Coordinates = { lng: number; lat: number };
export type RouteGeometry = { type: "LineString"; coordinates: [number, number][] };

type GeoJsonSource = { setData: (data: unknown) => void };
type MapboxMap = {
  addControl: (control: unknown, position?: string) => void;
  addLayer: (layer: Record<string, unknown>) => void;
  addSource: (id: string, source: Record<string, unknown>) => void;
  easeTo: (options: Record<string, unknown>) => void;
  fitBounds: (bounds: unknown, options?: Record<string, unknown>) => void;
  getSource: (id: string) => GeoJsonSource | undefined;
  on: (event: string, listener: () => void) => void;
  remove: () => void;
};
type MapboxMarker = {
  addTo: (map: MapboxMap) => MapboxMarker;
  remove: () => void;
  setLngLat: (coordinates: [number, number]) => MapboxMarker;
};
type MapboxGl = {
  accessToken: string;
  Map: new (options: Record<string, unknown>) => MapboxMap;
  Marker: new (options?: Record<string, unknown>) => MapboxMarker;
  NavigationControl: new (options?: Record<string, unknown>) => unknown;
  LngLatBounds: new () => { extend: (coordinates: [number, number]) => unknown };
};

declare global {
  interface Window {
    mapboxgl?: MapboxGl;
  }
}

let loader: Promise<MapboxGl> | null = null;

function loadMapbox(): Promise<MapboxGl> {
  if (window.mapboxgl) return Promise.resolve(window.mapboxgl);
  if (loader) return loader;

  loader = new Promise((resolve, reject) => {
    if (!document.getElementById("valley-mapbox-css")) {
      const link = document.createElement("link");
      link.id = "valley-mapbox-css";
      link.rel = "stylesheet";
      link.href = `https://api.mapbox.com/mapbox-gl-js/v${MAPBOX_GL_JS_VERSION}/mapbox-gl.css`;
      document.head.appendChild(link);
    }

    const finish = () =>
      window.mapboxgl
        ? resolve(window.mapboxgl)
        : reject(new Error("Mapbox GL JS não inicializou."));

    const existing = document.getElementById("valley-mapbox-js") as HTMLScriptElement | null;
    if (existing) {
      existing.addEventListener("load", finish, { once: true });
      existing.addEventListener("error", () => reject(new Error("Falha ao carregar o SDK Mapbox.")), { once: true });
      return;
    }

    const script = document.createElement("script");
    script.id = "valley-mapbox-js";
    script.src = `https://api.mapbox.com/mapbox-gl-js/v${MAPBOX_GL_JS_VERSION}/mapbox-gl.js`;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.addEventListener("load", finish, { once: true });
    script.addEventListener("error", () => reject(new Error("Falha ao carregar o SDK Mapbox.")), { once: true });
    document.head.appendChild(script);
  });

  return loader;
}

function point(value?: Coordinates): [number, number] | null {
  return value && Number.isFinite(value.lng) && Number.isFinite(value.lat)
    ? [value.lng, value.lat]
    : null;
}

function bearingBetween(start: Coordinates, end: Coordinates) {
  const startLat = (start.lat * Math.PI) / 180;
  const endLat = (end.lat * Math.PI) / 180;
  const deltaLng = ((end.lng - start.lng) * Math.PI) / 180;
  const y = Math.sin(deltaLng) * Math.cos(endLat);
  const x = Math.cos(startLat) * Math.sin(endLat) - Math.sin(startLat) * Math.cos(endLat) * Math.cos(deltaLng);
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
}

function friendlyError(cause: unknown) {
  const raw = cause instanceof Error ? cause.message : String(cause || "Mapa indisponível.");
  if (/401|unauthorized/i.test(raw)) return "Token Mapbox ausente, expirado ou revogado.";
  if (/403|forbidden/i.test(raw)) return "Token Mapbox bloqueado por escopo ou restrição de origem.";
  return raw;
}

type Props = {
  accessToken: string;
  current?: Coordinates;
  origin?: Coordinates;
  destination?: Coordinates;
  geometry?: RouteGeometry;
  routeLabel: string;
};

export default function MapboxRouteMap({ accessToken, current, origin, destination, geometry, routeLabel }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapboxMap | null>(null);
  const markersRef = useRef<MapboxMarker[]>([]);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const styleUri = useMemo(() => resolveNavigationStyleUri(), []);
  const credentialStatus = tokenStatus(accessToken);
  const modeLabel = styleUri === MAPBOX_STYLE_NIGHT ? "Navegação noturna" : "Navegação diurna";

  useEffect(() => {
    if (credentialStatus !== "ready" || !containerRef.current || mapRef.current) return;

    let active = true;
    void loadMapbox()
      .then((mapboxgl) => {
        if (!active || !containerRef.current) return;
        mapboxgl.accessToken = accessToken;
        const map = new mapboxgl.Map({
          container: containerRef.current,
          style: styleUri,
          center: [-44.1987, -19.9673],
          zoom: 14,
          pitch: 45,
          bearing: 0,
          antialias: true,
          attributionControl: true,
          cooperativeGestures: true,
        });
        map.addControl(
          new mapboxgl.NavigationControl({ showCompass: true, showZoom: true, visualizePitch: true }),
          "top-right",
        );
        map.on("load", () => {
          if (!active) return;
          setReady(true);
          setError("");
        });
        mapRef.current = map;
      })
      .catch((cause: unknown) => active && setError(friendlyError(cause)));

    return () => {
      active = false;
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = [];
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [accessToken, credentialStatus, styleUri]);

  useEffect(() => {
    const map = mapRef.current;
    const mapboxgl = window.mapboxgl;
    if (!ready || !map || !mapboxgl) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    const points: [number, number][] = [];
    const markerDefinitions = [
      { value: current, color: MAPBOX_COLORS.rider },
      { value: origin, color: MAPBOX_COLORS.pickup },
      { value: destination, color: MAPBOX_COLORS.destination },
    ] as const;

    markerDefinitions.forEach(({ value, color }) => {
      const coordinates = point(value);
      if (!coordinates) return;
      points.push(coordinates);
      markersRef.current.push(new mapboxgl.Marker({ color, scale: 0.88 }).setLngLat(coordinates).addTo(map));
    });

    if (geometry?.coordinates.length) {
      const data = { type: "Feature", properties: { provider: "mapbox", product: "valley-rider" }, geometry };
      const source = map.getSource("valley-route");
      if (source) {
        source.setData(data);
      } else {
        map.addSource("valley-route", { type: "geojson", data });
        map.addLayer({
          id: "valley-route-casing",
          type: "line",
          source: "valley-route",
          layout: { "line-join": "round", "line-cap": "round" },
          paint: {
            "line-color": MAPBOX_COLORS.routeCasing,
            "line-width": ["interpolate", ["linear"], ["zoom"], 10, 7, 16, 13],
            "line-opacity": 0.9,
          },
        });
        map.addLayer({
          id: "valley-route-line",
          type: "line",
          source: "valley-route",
          layout: { "line-join": "round", "line-cap": "round" },
          paint: {
            "line-color": MAPBOX_COLORS.route,
            "line-width": ["interpolate", ["linear"], ["zoom"], 10, 4, 16, 8],
            "line-opacity": 0.98,
          },
        });
      }
      geometry.coordinates.forEach((coordinates) => points.push(coordinates));
    }

    const target = destination || origin;
    if (current && target) {
      map.easeTo({
        center: [current.lng, current.lat],
        zoom: 15.5,
        pitch: 52,
        bearing: bearingBetween(current, target),
        duration: 650,
        padding: { top: 82, right: 42, bottom: 116, left: 42 },
      });
      return;
    }

    if (points.length) {
      const bounds = new mapboxgl.LngLatBounds();
      points.forEach((coordinates) => bounds.extend(coordinates));
      map.fitBounds(bounds, {
        padding: { top: 82, right: 42, bottom: 116, left: 42 },
        maxZoom: 16,
        duration: 650,
      });
    }
  }, [current, destination, geometry, origin, ready]);

  if (credentialStatus !== "ready") {
    return (
      <div className="map-empty" role="status">
        <strong>Mapbox aguardando configuração segura</strong>
        <span>{mapboxCredentialMessage(accessToken)}</span>
        <small>GPS, distância e ETA permanecem em contingência até a credencial pública ser injetada.</small>
      </div>
    );
  }

  return (
    <div className="map-shell" aria-label={routeLabel}>
      <div ref={containerRef} className="map-canvas" />
      <div className="map-brand">
        <img
          src="/brand/valley-riders-logo-official.png"
          alt=""
          aria-hidden="true"
          onError={(event) => {
            event.currentTarget.hidden = true;
          }}
        />
        <span className="map-brand-copy">
          <strong>VALLEY RIDER</strong>
          <span>Navegação operacional</span>
        </span>
      </div>
      {!ready && !error && <div className="map-overlay">Carregando mapa, trânsito e rota...</div>}
      {error && <div className="map-overlay map-error" role="alert">{error}</div>}
      <div className="map-legend" aria-hidden="true">
        <span><i className="dot rider" />Você</span>
        <span><i className="dot pickup" />Coleta</span>
        <span><i className="dot destination" />Destino</span>
      </div>
      <div className="map-guidance">
        <span>
          <strong>{routeLabel}</strong>
          <small>Rota priorizada com trânsito e câmera orientada</small>
        </span>
        <b>MAPBOX</b>
      </div>
      <div className="map-mode">{modeLabel}</div>
    </div>
  );
}
