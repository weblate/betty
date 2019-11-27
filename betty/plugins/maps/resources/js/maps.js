'use strict'

import mapsStyle from './maps.css' // eslint-disable-line no-unused-vars

import * as L from 'leaflet'
import leafletStyle from 'leaflet/dist/leaflet.css' // eslint-disable-line no-unused-vars
import leafletMarkerIconImage from 'leaflet/dist/images/marker-icon.png'
import leafletMarkerIcon2xImage from 'leaflet/dist/images/marker-icon-2x.png'
import leafletMarkerShadowImage from 'leaflet/dist/images/marker-shadow.png'
import places from './places.json'
import configuration from './configuration.js'

let mapCount = 0

function initializePlaceLists () {
  const placeLists = document.getElementsByClassName('places')
  for (let placeList of placeLists) {
    initializePlaceList(placeList)
  }
}

function initializePlaceList (placeList) {
  const placeData = placeList.querySelectorAll('[data-betty-place-id]')

  const mapArea = placeList.getElementsByClassName('map')[0]
  mapArea.id = (++mapCount).toString()

  let map = L.map(mapArea.id)

  // Build the attribution layer.
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map)

  // Build place markers.
  const markers = []
  for (let placeDatum of placeData) {
    if (placeDatum.dataset.bettyPlaceId in places) {
      let coordinates = places[placeDatum.dataset.bettyPlaceId]
      let marker = L.marker([coordinates.latitude, coordinates.longitude], {
        icon: new BettyIcon()
      }).addTo(map)
      marker.bindPopup(placeDatum.innerHTML)
      markers.push(marker)
    }
  }

  // Set the map's position and zoom level.
  const markerGroup = L.featureGroup(markers)
  map.fitBounds(markerGroup.getBounds(), {
    maxZoom: 9
  })
}

let BettyIcon = L.Icon.Default.extend({
  options: {
    imagePath: configuration.rootPath,
    iconUrl: leafletMarkerIconImage.replace(/^\/+/, ''),
    iconRetinaUrl: leafletMarkerIcon2xImage.replace(/^\/+/, ''),
    shadowUrl: leafletMarkerShadowImage.replace(/^\/+/, '')
  }
})

export {
  initializePlaceLists as betty
}
