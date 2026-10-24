"""
Standard RFC 7946 GeoJSON Exporter for GIS Integration (QGIS, ArcGIS, State Portal)
"""

from typing import List, Dict, Any

class GeoJSONExporter:
    @staticmethod
    def generate_geojson(hotspots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Converts hotspot cluster indicators into standard GeoJSON FeatureCollection.
        """
        features = []
        for spot in hotspots:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [spot["lon"], spot["lat"]]
                },
                "properties": {
                    "district_id": spot["district_id"],
                    "district_name": spot["district_name"],
                    "alert_level": spot["alert_level"],
                    "color": spot["color"],
                    "max_z_score": spot["max_z_score"],
                    "population": spot["population"],
                    "phcs_count": spot["phcs_count"],
                    "active_flags": spot["flagged_syndromes"]
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": features
        }
