# -*- coding: utf-8 -*-
"""Git_Project_NYC.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uztMAwr8SN3IOcMH7efq8za5GNcrzQpY

<h1>Objective</h1>
This dataset contains properties sold in New York City over a 12-month period from September 2016 to September 2017. The objective is to build a model to predict sale value in the future.

# Loading Dataset
"""

#Download dataset
!wget -q https://www.dropbox.com/s/6tc7e6rc395c7jz/nyc-property-sales.zip

#Unzip the data
!unzip nyc-property-sales.zip > /dev/null; echo " done."

"""# Importing Modules"""

#Import basic packages

import pandas as pd 
pd.set_option('display.max_rows', 100)
pd.reset_option('display.max_rows')

import warnings
warnings.filterwarnings("ignore")
import time              
import numpy as np
import pickle

from sklearn.model_selection import train_test_split                            #splitting data
from pylab import rcParams
from sklearn.linear_model import LinearRegression                               #linear regression
from sklearn.metrics.regression import mean_squared_error                       #error metrics
from sklearn.metrics import mean_absolute_error

import seaborn as sns                                                           #visualisation
import matplotlib.pyplot as plt                                                 #visualisation

# %matplotlib inline     
sns.set(color_codes=True)

"""# Exploaratory Data Analysis

**Reading Data**
"""

# Read data through Pandas and compute time taken to read

t_start = time.time()
df_prop = pd.read_csv('nyc-rolling-sales.csv')
t_end = time.time()
print('Time to Load Data: {} s'.format(t_end-t_start))                          # time [s]

df_prop.columns

df_prop.head(10)

#Let's have a look into the total number of columns and observations in the dataset
df_prop.info()

#Let's look into summary statistics of data
df_prop.describe().T

"""**Observation:**
- There is a column called Unnamed: 0 which is not required as it contains only continuous index numbers
- The datatypes of saleprice is not correct because the summary statistics of sale price is not displayed

Hence there is a lot of data cleaning to perform.

**Statistical Insight Using Pandas profiling**
"""

#Perform Pandas profiling to understand quick overview of columns

import pandas_profiling
report = pandas_profiling.ProfileReport(df_prop)
#covert profile report as html file
report.to_file("property_data.html")

from IPython.display import display,HTML,IFrame

display(HTML(open('property_data.html').read()))

"""**Drop**: -> Either not important to be used ; no inherent information; High Correlated Values

- Address
- Appartment Number
- ID
- Easement
- ZIP
- Total Units Skewed: - > Not Done Anything so far; However - > We do Numerical Transformations like - LOG ; High skew to Normal Distribution
- COMMERCIAL UNITS
- RESIDENTIAL UNITS
- High Skewed
- RESIDENTIAL UNITS
- Commercial Units
- borough
- Queens seems to have huge skewed data in terms of total unit
- Total Units is skewed ( some large values)

**DataType Conversion:** From a value prospective (domain dependent)

- Tax Class at time of sale
- Tax class t present
- Land Square Feet
- Gross Square feet
- Sales Price
- Borough
- Sale Date

**Removal of Unnecesary Data:** Data where the ranges or values are not in accordance of Domain High Zero's: ( Non Availability of Data)

- Total Unit
- Year Built
- ZIP - removed
- GROSS SQUARE FEET
- LAND SQUARE FEET Dash Substitute ( Non Availability of Data) - Done
- Sales Price
- GROSS SQUARE FEET
- LAND SQUARE FEET Action: — Done
- Remove 0, - & 10 rows from Sales Price

**Outliers:** Values beyond particular domain range

- Remove everything beyond 90 percentile in Sales Column

**Feature Engineering :** Gives us new features from old data

- Extract individual time features from time column
"""

#This column has no significance other than being an iterator
del df_prop['Unnamed: 0']
#This column has no significant value
del df_prop['EASE-MENT']

"""**Observation:**

- From Pandas profiling we understand SALE PRICEcolumns have string value in some rows and thus has to be removed.
- From Pandas Profiling we understand LAND SQUARE FEET and GROSS SQUARE FEET columns have string values which have to replaced by appropriate values
"""

df_prop['SALE PRICE'] = df_prop['SALE PRICE'].replace(' -  ',np.nan)
df_prop.dropna(inplace=True)

df_prop['LAND SQUARE FEET'] = df_prop['LAND SQUARE FEET'].replace(' -  ',np.nan)
df_prop['GROSS SQUARE FEET'] = df_prop['GROSS SQUARE FEET'].replace(' -  ',np.nan)

# count the number of NaN values in each column
print(df_prop.isnull().sum())

## Define a function impute_median and fill land square feet and gross square feet with median values
def impute_median(series):
    return series.fillna(series.median())

df_prop['LAND SQUARE FEET'] = df_prop['LAND SQUARE FEET'].transform(impute_median)
df_prop['GROSS SQUARE FEET'] = df_prop['GROSS SQUARE FEET'].transform(impute_median)

#Convert few column datatypes into appropriate ones for conserving memory

df_prop['TAX CLASS AT TIME OF SALE'] = df_prop['TAX CLASS AT TIME OF SALE'].astype('category')
df_prop['TAX CLASS AT PRESENT'] = df_prop['TAX CLASS AT PRESENT'].astype('category')
df_prop['LAND SQUARE FEET'] = pd.to_numeric(df_prop['LAND SQUARE FEET'], errors='coerce')
df_prop['GROSS SQUARE FEET']= pd.to_numeric(df_prop['GROSS SQUARE FEET'], errors='coerce')
df_prop['SALE PRICE'] = pd.to_numeric(df_prop['SALE PRICE'], errors='coerce')
df_prop['BOROUGH'] = df_prop['BOROUGH'].astype('category')

#The datatypes have now been changed
df_prop.info()

# Let's remove sale price with a nonsensically small dollar amount: $0 most commonly. 
# Since these sales are actually transfers of deeds between parties: for example, parents transferring ownership to their home to a child after moving out for retirement.

df_prop = df_prop[df_prop['SALE PRICE']!=0]

#Let's also remove observations that have gross square feet less than 400 sq. ft
#Let's also remove observations that have gross square feet less than 400 sq. ft
#Let's also remove observations that have sale price less than 1000 dollars


df_prop = df_prop[df_prop['GROSS SQUARE FEET']>400]   
df_prop = df_prop[df_prop['LAND SQUARE FEET']>400]
df_prop = df_prop[df_prop['SALE PRICE']>1000]

"""**Observation:**
- The most expensive property in NYC is a whopping 2 billion dollars which can be considered as an outlier.
"""

df_prop[df_prop['SALE PRICE']==2210000000]

#Let's also remove Outliers from the observations that have sale price greater than 99 percentile

q = df_prop["SALE PRICE"].quantile(0.99)
q

df_prop = df_prop[df_prop["SALE PRICE"] < q]
df_prop_lin = df_prop.copy()

# Convert sale date into time,month,year and day
df_prop['SALE DATE']=pd.to_datetime(df_prop['SALE DATE'])
df_prop['year']=df_prop['SALE DATE'].dt.year
df_prop['month']=df_prop['SALE DATE'].dt.month
df_prop['day']=df_prop['SALE DATE'].dt.day
df_prop['time']=df_prop['SALE DATE'].dt.hour
df_prop['day_week']=df_prop['SALE DATE'].dt.weekday_name

"""# Data Visualisation"""

#Assign numbered bouroughs to bourough names
dic = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn', 4: 'Queens', 5:'Staten Island'}
df_prop["borough_name"] = df_prop["BOROUGH"].apply(lambda x: dic[x])

# Count of properties in NYC in each bororugh
# %matplotlib inline
df_prop.borough_name.value_counts().nlargest(10).plot(kind='bar', figsize=(10,5))
plt.title("Number of properties by city")
plt.ylabel('Number of properties')
plt.xlabel('City');
plt.show()

# Distribution of Sale Price
df_prop['SALE PRICE'].describe()

"""**Observation:**
- The maximum sale price is 15 million
"""

df_prop['SALE PRICE'].plot.hist(bins=20, figsize=(12, 6), edgecolor = 'white')
plt.xlabel('price', fontsize=12)
plt.title('Price Distribution', fontsize=12)
plt.show()

"""**Observation:**
- The distribution is highly skewed towards the right which implies there are lesser properties that have a very high prices.
"""

df_prop["log_price"] = np.log(df_prop["SALE PRICE"] + 1)
df_prop_lin["log_price"] = np.log(df_prop["SALE PRICE"] + 1)
df_prop["log_price"].plot.hist(bins=20, figsize=(12, 6), edgecolor = 'white')
plt.xlabel('Logprice', fontsize=12)
plt.title('Price Distribution', fontsize=12)
plt.show()

df_prop["log_price"] = np.log(df_prop["SALE PRICE"] + 1)
sns.boxplot(df_prop.log_price)

#skewness and kurtosis
print("Skewness: %f" % df_prop['SALE PRICE'].skew())
print("Kurtosis: %f" % df_prop['SALE PRICE'].kurt())

#skewness and kurtosis
print("Skewness: %f" % df_prop['log_price'].skew())
print("Kurtosis: %f" % df_prop['log_price'].kurt())

# Co-relation Heat Map
plt.figure(figsize=(15,10))
c = df_prop[df_prop.columns.values[0:19]].corr()
sns.heatmap(c,cmap="BrBG",annot=True)

"""**Observation:**
- The heat map illustrates that sale price is independent of all column values that could be considered for linear regression.
"""

# Installing Module
!pip -q install plotly-express

# Code for displaying plotly express plots inline in colab
def configure_plotly_browser_state():
  import IPython
  display(IPython.core.display.HTML('''
        <script src="/static/components/requirejs/require.js"></script>
        <script>
          requirejs.config({
            paths: {
              base: '/static/base',
              plotly: 'https://cdn.plot.ly/plotly-latest.min.js?noext',
            },
          });
        </script>
        '''))
  
import plotly_express as px

configure_plotly_browser_state()
px.scatter(df_prop, x="GROSS SQUARE FEET", y="SALE PRICE", size ="TOTAL UNITS" ,color="borough_name",
           hover_data=["BUILDING CLASS CATEGORY","LOT"], log_x=True, size_max=60)

"""**Observation:**

- Properties with more total units do not fetch larger sales price
Properties in Staten Island have comparitively lesser sales price in comparison with other boroughs in New york city
"""

configure_plotly_browser_state()
px.box(df_prop, x="borough_name", y="SALE PRICE", color="TAX CLASS AT TIME OF SALE",hover_data=['NEIGHBORHOOD', 'BUILDING CLASS CATEGORY'],notched=True)

"""**Observation:**

- Manhatten has the highest priced properties that have a tax class 1 representing residential property of up to three units (such as one-,two-, and three-family homes and small stores or offices with one or two attached apartments) as compared to other boroughs.
- Properties in Staten Island have comparitively lesser sales price in comparison with other boroughs in New york city
"""

configure_plotly_browser_state()
px.box(df_prop, x="SALE PRICE", notched=True, hover_data=['borough_name'], orientation='h')

configure_plotly_browser_state()
px.box(df_prop, x="day_week", y="SALE PRICE", color="TAX CLASS AT TIME OF SALE", notched=True)

"""**Observation:**

On *Saturdays* there are no sales for the tax class 4 which represents properties such as such as offices, factories, warehouses, garage buildings, etc.

# Model Building
"""

df_prop_lin.columns

#Dropping few columns
del df_prop_lin['BUILDING CLASS AT PRESENT']
del df_prop_lin['BUILDING CLASS AT TIME OF SALE']
del df_prop_lin['NEIGHBORHOOD']
del df_prop_lin['ADDRESS']
del df_prop_lin['SALE DATE']
del df_prop_lin['APARTMENT NUMBER']
del df_prop_lin['RESIDENTIAL UNITS']
del df_prop_lin['COMMERCIAL UNITS']
del df_prop_lin['SALE PRICE']
del df_prop_lin['ZIP CODE']

#Select the variables to be one-hot encoded
one_hot_features = ['BOROUGH', 'BUILDING CLASS CATEGORY','TAX CLASS AT PRESENT','TAX CLASS AT TIME OF SALE']
# Convert categorical variables into dummy/indicator variables (i.e. one-hot encoding).
one_hot_encoded = pd.get_dummies(df_prop_lin[one_hot_features],drop_first=True)
one_hot_encoded.info(verbose=True, memory_usage=True, null_counts=True)

df_prop_lin.head(5)

one_hot_encoded.head(5)

# Replacing categorical columns with dummies
fdf = df_prop_lin.drop(one_hot_features,axis=1)
fdf = pd.concat([fdf, one_hot_encoded] ,axis=1)

fdf.head(5)

fdf.info()

#Standardize rows into uniform scale

X = fdf.drop(['log_price'],axis=1) 
y = fdf['log_price']

# [X,Y]  -> Feature Vector 

# Scale the values 
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X)
fdf_normalized = scaler.transform(X)
# Scale and center the data


# Create a pandas DataFrame
fdf_normalized = pd.DataFrame(data=fdf_normalized, index=X.index, columns=X.columns)

fdf_normalized.head(5)

"""**Split the data into train and test**"""

X_train, X_test, y_train, y_test = train_test_split(X,y)

"""**Train the model**"""

# initialize the model
lr= LinearRegression()

# fit the model
model_fit=lr.fit(X_train,y_train)

from sklearn.externals import joblib 
  
# Save the model as a pickle in a file 
joblib.dump(model_fit, 'model.pkl')

# Train Accuracy 

#predict on train data
train_pred = model_fit.predict(X_train)

#mean squared error
mse=mean_squared_error(y_train,train_pred)

#root mean squared error
print('train rmse: {}'.format(np.sqrt(mse)))

#mean absolute error
mae=mean_absolute_error(y_train,train_pred)
print('train mae: {}'.format(mae))

"""**Test the model**"""

#predict on test data
test_pred = model_fit.predict(X_test)

#mean squared error
mse=mean_squared_error(y_test,test_pred)

#root mean squared error
print('test rmse: {}'.format(np.sqrt(mse)))

#mean absolute error
mae=mean_absolute_error(y_train,train_pred)
print('test mae: {}'.format(mae))