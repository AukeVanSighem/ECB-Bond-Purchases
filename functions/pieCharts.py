import matplotlib.pyplot as plt

# Put the percentage of each sector in the pie chart if the value is bigger than 2.4
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        if (pct > 2.4):
            return '{p:.2f}%'.format(p=pct)
        else:
            return ''
    return my_autopct

# Get all the sectors of a given type in decending order based on the number of times a bond was bought for this sector.
def get_all_sectors(sector_type, sector_mappings):
    sector_mappings['number']=1
    sectors = sector_mappings[[sector_type, 'number']].groupby([sector_type]).sum()
    sectors = sectors.sort_values("number", axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None)
    return sectors

# Create a pie chart to represent the number of times an industry, sector or supersector is present in the data
# (multiple bonds for the same company are counted separately)    
def make_pie_chart(column_name, sector_mappings):
    fig = plt.figure(figsize=(9,9))
    ax = plt.subplot(111)

    sectors = get_all_sectors(column_name, sector_mappings)
    
    sectors.plot(kind='pie', y='number', ax=ax, autopct=make_autopct(sectors['number']), fontsize=12, legend=False, rotatelabels=True, pctdistance=0.8)
    plt.axis("off")
    plt.title(column_name+"\n\n\n")