import { useEffect, useRef, useState } from "react";

export type Coordinates = { lng: number; lat: number };
export type RouteGeometry = { type: "LineString"; coordinates: [number, number][] };

type GeoJsonSource = { setData: (data: unknown) => void };
type MapboxMap = {
  addControl: (control: unknown, position?: string) => void;
  addLayer: (layer: Record<string, unknown>) => void;
  addSource: (id: string, source: Record<string, unknown>) => void;
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
  NavigationControl: new () => unknown;
  LngLatBounds: new () => { extend: (coordinates: [number, number]) => unknown };
};

declare global { interface Window { mapboxgl?: MapboxGl } }
let loader: Promise<MapboxGl> | null = null;

function loadMapbox(): Promise<MapboxGl> {
  if (window.mapboxgl) return Promise.resolve(window.mapboxgl);
  if (loader) return loader;
  loader = new Promise((resolve, reject) => {
    if (!document.getElementById("valley-mapbox-css")) {
      const link = document.createElement("link");
      link.id = "valley-mapbox-css";
      link.rel = "stylesheet";
      link.href = "https://api.mapbox.com/mapbox-gl-js/v3.25.0/mapbox-gl.css";
      document.head.appendChild(link);
    }
    const finish = () => window.mapboxgl ? resolve(window.mapboxgl) : reject(new Error("Mapbox não inicializou."));
    const existing = document.getElementById("valley-mapbox-js") as HTMLScriptElement | null;
    if (existing) { existing.addEventListener("load", finish); existing.addEventListener("error", () => reject(new Error("Falha ao carregar Mapbox."))); return; }
    const script = document.createElement("script");
    script.id = "valley-mapbox-js";
    script.src = "https://api.mapbox.com/mapbox-gl-js/v3.25.0/mapbox-gl.js";
    script.async = true;
    script.addEventListener("load", finish);
    script.addEventListener("error", () => reject(new Error("Falha ao carregar Mapbox.")));
    document.head.appendChild(script);
  });
  return loader;
}

function point(value?: Coordinates): [number, number] | null {
  return value && Number.isFinite(value.lng) && Number.isFinite(value.lat) ? [value.lng, value.lat] : null;
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

  useEffect(() => {
    if (!accessToken || !containerRef.current || mapRef.current) return;
    let active = true;
    void loadMapbox().then((mapboxgl) => {
      if (!active || !containerRef.current) return;
      mapboxgl.accessToken = accessToken;
      const map = new mapboxgl.Map({ container: containerRef.current, style: "mapbox://styles/mapbox/navigation-night-v1", center: [-44.2, -19.92], zoom: 13, attributionControl: true });
      map.addControl(new mapboxgl.NavigationControl(), "top-right");
      map.on("load", () => active && setReady(true));
      mapRef.current = map;
    }).catch((cause: unknown) => active && setError(cause instanceof Error ? cause.message : "Mapa indisponível."));
    return () => { active = false; markersRef.current.forEach((marker) => marker.remove()); markersRef.current = []; mapRef.current?.remove(); mapRef.current = null; };
  }, [accessToken]);

  useEffect(() => {
    const map = mapRef.current;
    const mapboxgl = window.mapboxgl;
    if (!ready || !map || !mapboxgl) return;
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];
    const points: [number, number][] = [];
    ([{ value: current, color: "#00c2ff" }, { value: origin, color: "#f59e0b" }, { value: destination, color: "#22c55e" }] as const).forEach(({ value, color }) => {
      const coordinates = point(value);
      if (!coordinates) return;
      points.push(coordinates);
      markersRef.current.push(new mapboxgl.Marker({ color }).setLngLat(coordinates).addTo(map));
    });
    if (geometry?.coordinates.length) {
      const data = { type: "Feature", properties: {}, geometry };
      const source = map.getSource("valley-route");
      if (source) source.setData(data);
      else {
        map.addSource("valley-route", { type: "geojson", data });
        map.addLayer({ id: "valley-route-line", type: "line", source: "valley-route", layout: { "line-join": "round", "line-cap": "round" }, paint: { "line-color": "#8b5cf6", "line-width": 6, "line-opacity": 0.9 } });
      }
      geometry.coordinates.forEach((coordinates) => points.push(coordinates));
    }
    if (points.length) {
      const bounds = new mapboxgl.LngLatBounds();
      points.forEach((coordinates) => bounds.extend(coordinates));
      map.fitBounds(bounds, { padding: 52, maxZoom: 16, duration: 650 });
    }
  }, [current, destination, geometry, origin, ready]);

  if (!accessToken) return <div className="map-empty" role="status"><strong>Mapbox aguardando configuração</strong><span>Defina VITE_MAPBOX_ACCESS_TOKEN. GPS, distância e ETA continuam em contingência.</span></div>;
  return <div className="map-shell" aria-label={routeLabel}><div ref={containerRef} className="map-canvas" />{!ready && !error && <div className="map-overlay">Carregando mapa e rota...</div>}{error && <div className="map-overlay map-error">{error}</div>}<div className="map-legend" aria-hidden="true"><span><i className="dot rider" />Você</span><span><i className="dot pickup" />Coleta</span><span><i className="dot destination" />Destino</span></div></div>;
}
