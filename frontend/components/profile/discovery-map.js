"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";

export function DiscoveryMap({ creators }) {
  const mapRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;
    if (!token || !containerRef.current) {
      return undefined;
    }

    mapboxgl.accessToken = token;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [78.9629, 22.5937],
      zoom: 3.4
    });

    creators
      .filter((creator) => creator.creatorProfile?.longitude && creator.creatorProfile?.latitude)
      .forEach((creator) => {
        new mapboxgl.Marker({ color: "#0f766e" })
          .setLngLat([creator.creatorProfile.longitude, creator.creatorProfile.latitude])
          .setPopup(new mapboxgl.Popup({ offset: 24 }).setHTML(`<strong>${creator.name}</strong><p>${creator.creatorProfile.niche}</p>`))
          .addTo(map);
      });

    mapRef.current = map;
    return () => map.remove();
  }, [creators]);

  if (!process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN) {
    return <div className="rounded-3xl bg-white/70 p-6 text-sm text-[var(--muted)]">Add `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN` to render the live discovery map.</div>;
  }

  return <div ref={containerRef} className="h-[360px] rounded-3xl" />;
}
