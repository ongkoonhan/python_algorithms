# https://hackernoon.com/computer-graphics-scan-line-polygon-fill-algorithm-3cb47283df6

# Generator that yields (x,y) points within a polygon based on a set of sorted input vertices


class ScanLinePolygonFill:
    
    def __init__(self, vertices):
        self.edge_table = []
        self.active_list = []

        # Assume vertices are ordered from left to right
        # For each Edge, Vertices are ordered from left to right (smaller x coordinate on left)
        for i in range(len(vertices)):
            pt1, pt2 = vertices[i-1], vertices[i]
            edge = (pt1, pt2) if pt1[0] <= pt2[0] else (pt2, pt1)

            y_list = [pt1[1], pt2[1]]
            dx = edge[1][0] - edge[0][0]
            dy = edge[1][1] - edge[0][1]

            if dy == 0:   # Horizontal lines (ignored)
                continue
            if dx == 0:   # Vertical lines
                slope = 0
            elif dy/dx < 0:
                slope = -1
            else:
                slope = 1

            edge_bucket = dict(
                id = i,
                y_max = max(y_list),
                y_min = min(y_list),
                x = pt1[0] if pt1[1] <= pt2[1] else pt2[0],
                sign = -1 if slope < 0 else 1,
                dx = abs(dx),
                dy = abs(dy),
                sum = 0,
                edge = edge,
            )
            self.edge_table.append(edge_bucket)
        self.edge_table.sort(key=lambda e: e["y_min"])

    def iterate_fill_polygon_pts(self):
        try:
            scanline = self.edge_table[0]["y_min"]   # Initialize with first edge
            while len(self.edge_table) > 0:
                # Remove inactive edges that are past scanline
                to_remove = []
                for edge_bucket in self.active_list[:]:
                    if edge_bucket["y_max"] == scanline:
                        to_remove.append(edge_bucket["id"])
                        self.active_list.remove(edge_bucket)
                self.edge_table[:] = [edge_bucket for edge_bucket in self.edge_table if edge_bucket["id"] not in to_remove]

                # Add new active edges that meet scanline
                for edge_bucket in self.edge_table:
                    self.active_list.append(edge_bucket) if edge_bucket["y_min"] == scanline else None

                # Sort active edges
                self.active_list.sort(key=lambda e: e["x"])

                for i in range(0, len(self.active_list), 2):
                    edge1, edge2 = self.active_list[i], self.active_list[i+1]
                    for j in range(edge1["x"]+1, edge2["x"]):   # Don't fill on left side boundary line
                        yield (j,scanline)   # (x,y) pt to be processed by user

                # Update scanline and edge_buckets x-values
                scanline += 1
                for edge_bucket in self.active_list:
                    edge_bucket["sum"] += edge_bucket["dx"]
                    while edge_bucket["sum"] >= edge_bucket["dy"]:
                        edge_bucket["x"] += edge_bucket["sign"]
                        edge_bucket["sum"] -= edge_bucket["dy"]
        finally:
            return




