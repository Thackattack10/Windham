def project_golf_points_factory(driving_weight, putting_weight, form_weight):
    def project_golf_points(row):
        # Safely get values, defaulting to 0 if missing
        driving = row.get('Driving', 0)
        putting = row.get('Putting', 0)
        recent_form = row.get('RecentForm', 0)

        # Calculate weighted projection
        return (driving * driving_weight +
                putting * putting_weight +
                recent_form * form_weight)
    return project_golf_points
