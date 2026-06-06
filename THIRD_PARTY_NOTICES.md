# Third-Party Notices

This file summarizes third-party materials and external terms that may apply to `Russian-regions-puzzle`. It is an attribution and due-diligence aid, not a complete legal inventory.

## Map Data And Geometry

`Russian_regions_TopoJSON.topojson` contains the playable map geometry for 89 federal-subject features. The repository currently does not encode a detailed upstream provenance statement inside the data file. Treat the geometry as map data that may carry original provider terms. Before republishing, adapting or using it in a formal research dataset, verify and document the upstream source, license, date, boundary assumptions, simplification process and attribution requirements.

The repository's CC BY 4.0 content license applies only to repository-authored documentation, educational content and data where the project has rights to license it. It does not override third-party map-data terms.

## Runtime Libraries And Services

| Component | Use In This Project | Notice |
| --- | --- | --- |
| D3.js | Browser projection and geometry support via CDN and npm package | Copyright and license belong to the D3 authors. See package metadata in `node_modules/d3` or npm. |
| TopoJSON Client | Converts TopoJSON to GeoJSON in the browser | Copyright and license belong to the TopoJSON authors. See package metadata in `node_modules/topojson-client` or npm. |
| Firebase JavaScript SDK and Firebase Realtime Database | Optional leaderboard storage and result synchronization | Firebase SDK and service use are governed by Google/Firebase licenses and service terms. Database rules and data retention are the deployer's responsibility. |
| Playwright | Local browser tests | Governed by its package license and notices. |
| http-server | Optional local static server dependency | Governed by its package license and notices. |
| GitHub Pages | Static hosting for the public demo | Governed by GitHub terms for hosted content and service use. |

## Official, Institutional And Geographic Names

Names of countries, regions, federal subjects, federal districts, institutions, services and products are used for identification, education, interface labels and documentation. Their use does not imply endorsement by any government, institution, company or rights holder.

Geographic names and boundaries can be politically sensitive and may change over time. The project uses the labels and geometries present in the repository data file for educational gameplay. Contributors should document any boundary or naming updates and explain the source used.

## Visual And Generated Materials

Screenshots, diagrams and walkthrough media under `assets/visuals/` are project documentation assets unless otherwise noted. If a visual displays map geometry or third-party interface/service names, those underlying materials remain subject to their original terms.

## Contributor Responsibility

When adding data, images, translations, logos, institutional names or external examples, include enough provenance for review:

- source URL or bibliographic reference;
- license or terms of use;
- date accessed or data vintage;
- modifications made;
- attribution text required by the provider.
