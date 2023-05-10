function initMap() {
    // Define the locations and info windows for each map
    const locations = [{
            lat: 32.887425,
            lng: -6.914740,
            infoWindow: new google.maps.InfoWindow({
                content: "Click the map to get Lat/Lng for Form 1!",
            }),
        },
        {
            lat: 32.885122,
            lng: -6.911647,
            infoWindow: new google.maps.InfoWindow({
                content: "Click the map to get Lat/Lng for Form 2!",
            }),
        },
        {
            lat: 32.888950,
            lng: -6.918484,
            infoWindow: new google.maps.InfoWindow({
                content: "Click the map to get Lat/Lng for Form 3!",
            }),
        }
    ];

    // Create the maps and attach click listeners to each
    const maps = locations.map((location, index) => {
        const map = new google.maps.Map(document.getElementById(`map${index+1}`), {
            zoom: 14,
            center: location,
        });

        // Open the info window for this map
        location.infoWindow.setPosition(location);
        location.infoWindow.open(map);

        // Add a click listener to update the info window content
        map.addListener("click", (mapsMouseEvent) => {

            // Get the clicked coordinates
            const clickedLat = mapsMouseEvent.latLng.lat();
            const clickedLng = mapsMouseEvent.latLng.lng();

            // Update the input fields
            document.getElementById(`lat${index+1}`).value = clickedLat;
            document.getElementById(`lng${index+1}`).value = clickedLng;

            location.infoWindow.close();
            location.infoWindow = new google.maps.InfoWindow({
                position: mapsMouseEvent.latLng,
            });
            location.infoWindow.setContent(
                "📍"
            );
            location.infoWindow.open(map);
        });

        return map;
    });
}

window.initMap = initMap;