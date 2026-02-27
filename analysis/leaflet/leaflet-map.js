fetch('../../metadata_combined/flickr_commons_pictures.csv')
    .then(response => response.text())
    .then(csvText => {
        const { data, errors } = Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true,
            dynamicTyping: false,
            comments: false
        });

        if (errors.length > 0) {
            console.error('CSV parse errors:', errors);
            document.getElementById('stats').innerHTML = `CSV loaded with ${errors.length} parse warnings`;
        }

        // Filter valid geo data
        const geoData = data.filter(row => 
            row.latitude && row.longitude && 
            parseFloat(row.latitude) !== 0 && parseFloat(row.longitude) !== 0
        );

        // Create map
        const map = L.map('map').setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Custom red pin icon
        const customIcon = L.divIcon({
            className: 'pin-marker',
            html: '<div style="background: #ff0000; width: 20px; height: 20px; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%; border: 3px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>',
            iconSize: [26, 26], iconAnchor: [13, 26]
        });

        // Marker cluster group
        const markers = L.markerClusterGroup({
            maxClusterRadius: 50,
            iconCreateFunction: function(cluster) {
                return L.divIcon({
                    html: '<div style="background: #ff4444; color: white; border-radius: 50%; width: 30px; height: 30px; line-height: 30px; text-align: center; border: 3px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-weight: bold;">' + cluster.getChildCount() + '</div>',
                    iconSize: [36, 36], iconAnchor: [18, 18]
                });
            }
        });

        // Add markers
        geoData.forEach(row => {
            const lat = parseFloat(row.latitude);
            const lon = parseFloat(row.longitude);
            const title = row.title || 'No title';
            const institution = row.institution || 'Unknown';
            const imageUrl = row.image_url;

            const popupHtml = `
                <div style="font-family: Arial; max-width: 300px;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">${title}</h3>
                    <h4 style="margin: 0 0 15px 0; color: #666; font-weight: normal;">${institution}</h4>
                    ${imageUrl ? `<img src="${imageUrl}" style="max-width: 100%; height: auto; border-radius: 5px;" onerror="this.style.display='none'">` : ''}
                </div>
            `;

            const marker = L.marker([lat, lon], {icon: customIcon}).bindPopup(popupHtml);
            markers.addLayer(marker);
        });

        map.addLayer(markers);
        
        // Fit bounds to data
        if (markers.getLayers().length > 0) {
            map.fitBounds(markers.getBounds(), {padding: [20, 20]});
        }

        // Update stats
        document.getElementById('stats').innerHTML = 
            `${geoData.length.toLocaleString()} pictures with valid geo loaded`;
    })
    .catch(err => {
        document.getElementById('stats').innerHTML = 'Error loading CSV: ' + err.message;
        console.error('Fetch error:', err);
    });
