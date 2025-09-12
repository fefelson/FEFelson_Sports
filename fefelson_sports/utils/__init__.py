def _set_colors(self, value, analytics):
        # print(analytics)
        greater_than = lambda v, a: v > a
        less_than = lambda v, a: v < a

        colors = ["gold", "forestgreen", "springgreen", "khaki", "salmon", "red"]
        if analytics["best_value"] > analytics["worst_value"]:
            q_list = ["q9", "q8", "q6", "q4", "q2", "q1"]
            func = greater_than
        else:
            q_list = ["q1", "q2", "q4", "q6", "q8", "q9"]
            func = less_than

        background_color = "black"
        for idx, color in zip(q_list, colors):
            if func(value, analytics[idx]):
                background_color = color
                break

        text_color = "white" if background_color in ("red", "forestgreen", "black") else "black"
        return background_color, text_color