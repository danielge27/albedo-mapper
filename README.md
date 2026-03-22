# 🛰️ Boston Area Albedo Mapper
### *Team Cubeagle — Urban Heat Risk Analysis Tool*

> A low-cost, open-source tool that analyzes **surface reflectivity (albedo)** and **urban heat risk** from satellite imagery — built by high school students in the Boston area to support environmental justice research and city planning.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-albedo--mapper.onrender.com-00C8FF?style=for-the-badge&logo=render)](https://albedo-mapper.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-green?style=for-the-badge&logo=opencv)](https://opencv.org)

---

## 🌐 Live Website

**→ [https://albedo-mapper.onrender.com](https://albedo-mapper.onrender.com)**

> ⚠️ Hosted on Render free tier — may take 1–2 minutes to wake up on first visit.

---

## 📸 Demo

### 1. Search any Boston-area neighborhood

Enter any address or neighborhood name. The interactive satellite map loads instantly using ArcGIS World Imagery.

![Search and Map View](docs/screenshots/screenshot1.jpg)

---

### 2. Surface Analysis — Original vs. Albedo Contour Map

Click **Calculate Albedo** to run the analysis. The tool detects 6 surface types and color-codes each zone:

| Color | Surface | Albedo | Heat Risk |
|-------|---------|--------|-----------|
| 🔴 Red | Dark Tar Roof | 0.05 | CRITICAL |
| 🟠 Orange | Asphalt / Road | 0.10 | HIGH |
| 🟡 Yellow | Concrete / Sidewalk | 0.25 | MEDIUM |
| 🩵 Cyan | Bright / White Roof | 0.65 | LOW |
| 🟢 Green | Trees / Vegetation | 0.20 | BENEFICIAL |
| 🔵 Blue | Water Body | 0.06 | COOLING |

![Surface Analysis Contour Map](docs/screenshots/screenshot3.jpg)

---

### 3. Full Report with Planning Recommendations

The tool generates a complete heat risk report with a letter grade, specific recommendations, and policy suggestions for city planners.

![Full Report and Recommendations](docs/screenshots/screenshot2.jpg)

---

## 🔬 How It Works

```
User enters address
        ↓
ArcGIS satellite tile loaded into Leaflet map
        ↓
surface_detector.py  →  detects 6 surface types via HSV color analysis
        ↓
albedo_calculator.py →  calculates weighted albedo score + heat index
        ↓
report_generator.py  →  generates contour map + full PDF report
        ↓
Results displayed in browser + downloadable PNG report
```

### The Key Formulas

| Formula | What it calculates |
|---------|-------------------|
| `pixel_albedo = brightness ÷ 255` | Reflectivity of one pixel (0.0–1.0) |
| `avg_albedo = Σ(coverage% × albedo) ÷ total%` | Neighborhood-wide average reflectivity |
| `heat_index = (1 − avg_albedo) × 100` | Heat risk score (0 = cool, 100 = critical) |
| `excess_heat = (dark%×0.04) + (asphalt%×0.03) − (veg%×0.03)` | Estimated °F above ideal urban baseline |

---

## 🏙️ Community Impact

This tool was built to address a critical gap in urban climate data: **hyperlocal, street-level albedo measurements** that expensive satellites can't provide at neighborhood resolution.

### Target communities in Greater Boston:

| Neighborhood | Issue | Expected Finding |
|---|---|---|
| **Roxbury** | Urban heat island, environmental justice | 🔴 High concrete, low vegetation |
| **Seaport District** | New glass towers, concrete expansion | 🔴 Critical heat absorption |
| **Blue Hills / Milton** | Forest edge loss from suburban sprawl | 🟢 Cooling buffer at risk |
| **Jamaica Plain** | Mixed urban-green transition zone | 🟠 Medium intervention needed |
| **Back Bay** | Dense historic urban core | 🔴 High priority for green roofs |

---

## 🚀 Run Locally

### Prerequisites
```bash
Python 3.10+
pip
```

### Setup
```bash
# Clone the repository
git clone https://github.com/danielge27/albedo-mapper.git
cd albedo-mapper

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open your browser at **http://localhost:5000**

---

## 📁 Project Structure

```
albedo-mapper/
│
├── app.py                  # Flask web server + API routes
├── surface_detector.py     # HSV-based surface classification
├── albedo_calculator.py    # Albedo score + heat index formulas
├── report_generator.py     # matplotlib report generation
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment config
│
├── templates/
│   └── index.html          # Frontend map interface (Leaflet.js)
│
├── static/
│   └── images/             # Logo and static assets
│
└── docs/
    └── screenshots/        # Demo screenshots for README
```

---

## 🛠️ Built With

| Technology | Purpose |
|---|---|
| **Python / Flask** | Web server and API |
| **OpenCV** | Image processing and surface detection |
| **NumPy** | Pixel-level math and array operations |
| **Matplotlib** | Report generation and contour visualization |
| **Leaflet.js** | Interactive satellite map in the browser |
| **ArcGIS World Imagery** | Free high-resolution satellite tiles |
| **Render.com** | Cloud deployment (free tier) |

---

## 📊 Research Applications

This tool supports ongoing research into:

- **Albedo-Income Gap** — Does neighborhood wealth correlate with surface heat absorption?
- **Temporal Change Analysis** — How has Boston lost reflective surfaces over 20 years?
- **Green Roof ROI Modeling** — How many green roofs would meaningfully cool a neighborhood?
- **Satellite Validation** — How does ground-truth albedo compare to NASA MODIS satellite data?
- **Glass Building Heat Traps** — Quantifying reflected radiation from glass facades onto pedestrians

---

## 🏫 About Team Cubeagle

This project was developed by **Team Cubeagle**, a group of high school students in the Boston area, as part of the **BWSI (Beaver Works Summer Institute) CubeSat program**. The original concept was an orbital albedo measurement CubeSat — this web app extends that mission to ground-based, hyperlocal neighborhood analysis.

**Team members:** Charles He, Daniel Gao, Daniel Ge, Hanson Zhu

---

## 📄 License

MIT License — free to use, modify, and share with attribution.

---

## 🌱 Contributing

Pull requests welcome! Areas where help is especially appreciated:
- Additional surface type detection (green roofs, solar panels, permeable pavement)
- Historical image comparison (temporal albedo change)
- Census income data overlay for environmental justice analysis
- Mobile-responsive UI improvements

---

<div align="center">

**Built with 🛰️ by Team Cubeagle · Boston, MA**

[Live App](https://albedo-mapper.onrender.com) · [Report an Issue](https://github.com/danielge27/albedo-mapper/issues) · [Team Cubeagle](https://github.com/danielge27)

</div>
