### This exercise iniatially was about getting averages evolution on salaries trough the years and count employees by year.
### I decided it was too simple a analysis and tried some things to use a little bit more pandas tools to process information.
### The original DB was SQLite, so I adapted it to PostgreSQL, brought it to my code and experimented with dataframes and series.

### Import libraries
#
import pandas as pd
import numpy as np
import sqlalchemy
from IPython.display import display

#### Import DB
#
pwd = input('DB password: ')
salaries= pd.read_sql(sql= 'SELECT * FROM "Salaries"', con= (f'postgresql://postgres:{pwd}@localhost:5432/Salaries'), )
salaries.set_index('Id', inplace= True)

### 1. San Francisco Agency's employees:

# ### Adding 'pure' number columns to my dataframe
pay_year= salaries.loc[salaries['Agency'] == 'San Francisco']
pay_year= pay_year[['Year', 'TotalPay', 'Benefits', 'TotalPayBenefits']]
pay_year = pay_year.groupby('Year').sum()
pay_year.replace(0, np.nan, inplace= True)

# ### Starting my dataframe-row-to-be summary
summary = pay_year.sum()

# ### Now adding relative numbers to my dataframe
pay_year['GrowthPay'] = pay_year['TotalPay'].div(pay_year['TotalPay'].shift(1))
pay_year['GrowthBenefits'] = pay_year['Benefits'].div(pay_year['Benefits'].shift(1))
pay_year['GrowthPayBenefits'] = pay_year['TotalPayBenefits'].div(pay_year['TotalPayBenefits'].shift(1))

# ### Calculating percents between last valid index and first valid index for each payment category
summary['GrowthPay'] = (pay_year.loc[pay_year['TotalPay'].last_valid_index(), 'TotalPay'] / 
                        pay_year.loc[pay_year['TotalPay'].first_valid_index(), 'TotalPay'])
summary['GrowthBenefits'] = (pay_year['Benefits'].loc[pay_year['Benefits'].last_valid_index()] / 
                              pay_year['Benefits'].loc[pay_year['Benefits'].first_valid_index()])
summary['GrowthPayBenefits'] = (pay_year['TotalPayBenefits'].loc[pay_year['TotalPayBenefits'].last_valid_index()] / 
                                pay_year['TotalPayBenefits'].loc[pay_year['TotalPayBenefits'].first_valid_index()])

# ### Concatenate my Dataframe and my summary Series
pay_year = pd.concat([pay_year, summary.to_frame().T], ignore_index= False)
pay_year.rename(index= {pay_year.last_valid_index(): 'Summary'}, inplace= True)
pay_year.to_csv('test_concat_01.csv', sep= ';')

# ### As it seems Styler objects are not working on my VSCode, built this "turnaround"
#
def format_money(df_value):
    return '${:,.2f}'.format(df_value).replace(',', ' ')
def format_percent(df_value):
    return '{:-,.2%}'.format(df_value - 1).replace(',', ' ')
#
pay_year['TotalPay'] = pay_year['TotalPay'].apply(format_money)
pay_year['Benefits'] = pay_year['Benefits'].apply(format_money)
pay_year['TotalPayBenefits'] = pay_year['TotalPayBenefits'].apply(format_money)
pay_year['GrowthPay'] = pay_year['GrowthPay'].apply(format_percent)
pay_year['GrowthBenefits'] = pay_year['GrowthBenefits'].apply(format_percent)
pay_year['GrowthPayBenefits'] = pay_year['GrowthPayBenefits'].apply(format_percent)

display(pay_year)

#
# ### End of script