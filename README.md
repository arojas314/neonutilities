<div align="center" >


![](https://github.com/arojas314/neonutilities/tree/main/docs/_source/_static/NEON_image.png?raw=true)


# Download and display NEON data

<!-- Badges -->

<!-- [![](https://img.shields.io/pypi/v/goes2go)](https://pypi.python.org/pypi/goes2go/)
![](https://img.shields.io/github/license/blaylockbk/goes2go) -->

<!--(Badges)-->

</div>

The National Science Foundation's National Ecological Observatory Network (NEON) offers ecological data from sites across the United States through the [NEON Data Portal](https://data.neonscience.org/). **neonutilities** is a python package that makes it easy to find and download data to your local computer. We also provide some additional utilities to visualize and analyze the data.

<br>

📔 [neonutilities Documentation](https://arojas314.github.io/neonutilities/_build/html/)

<br>

---

# Capabilities

## Download Data

Download NEON data files to your local computer. Files can also be read into Pandas DataFrames.

Downloading data locally is as simple as importing the neonutilities package and using the `download_data` function with the product ID.

```python
import neonutilities as nu

# Download short wave radiation data
download_data('DP1.00024.001', "HARV", start="2019-01", end="2021-12")
```
