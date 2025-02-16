"""
Cost calculation using Ecoinvent38 price data
Author: Sander van Nielen
Date: October 2022
Contact: s.s.van.nielen@cml.leidenuniv.nl
"""

import pandas as pd
from bw2io import SingleOutputEcospold2Importer #Ecospold2DataExtractor

source = "C:/Users/nielenssvan/surfdrive/LCC/Ecoinvent38/datasets/00a7c4b9-d01d-4f77-b617-5d74a764815a_4da7438b-1508-4eb9-b58b-9e85fcf26801.spold" 
xml_data = source.open.read()
xml_df = pd.read_xml(source, xpath="/ecoSpold/childActivityDataset/flowData")

# Useful part starts here
# -----------------------
def get_price(exc):
    """Extract the price data from an exchange, convert to dict.
    """
    data = {'flow': exc['flow'], 'name': exc['name'], 'unit': exc['unit']}
    for item in ['amount', 'comment']:
        if item in exc['properties']['price']:
            data[item] = exc['properties']['price'][item]
    return data

def write_prices(data):
    Prices = []
    for act in data:
        for exc in act['exchanges']:
            if 'properties' in exc:
                if 'price' in exc['properties']:
                    Prices.append(get_price(exc))
                # new = {item: exc['properties'][item] for item in if item in exc['properties']}
                #Prices.append(new)
    return Prices

# metadata = Ecospold2DataExtractor.extract_technosphere_metadata("Ecoinvent38")
# new_data = Ecospold2DataExtractor.extract("Ecoinvent38", "cutoff38")
new_data = SingleOutputEcospold2Importer("Ecoinvent38/datasets", "cutoff38")
new_data.apply_strategies()
stats = new_data.statistics()
new_data.drop_unlinked(i_am_reckless=True)
new_data.write_database()
Prices = write_prices(new_data.data)
# new_data = None
price_df = pd.DataFrame(Prices).drop_duplicates(ignore_index=True)
price_df.to_csv("prices_ei38.csv", index=False)

# Calculating the minimum costs of a production chain
#------------------------------
import pandas as pd
import bw2data as bd
import bw2calc

def lcc(functional_unit, Prices, depth=1000, verbose=False):
    """Calculate the costs of all inputs needed to produce `functional_unit`.
    Restrict calculation to `depth` iterations.
    Returns Expenses (dict), foreground (list)
    """
    Expenses = {}
    foreground = {functional_unit._data['database']: []}
    heap = [(functional_unit, 1)] # Starting point of graph traversal
    while len(heap) > 0 and depth > 0:
        activity, demand = heap[0]
        for link in activity.technosphere():
            amount = link.amount * demand / [p for p in activity.production()][0].amount
            name = link.input['reference product']
            if name in Prices:
                if name not in Expenses: Expenses[name] = 0
                Expenses[name] = Expenses[name] + Prices[name] * amount
            else:
                db = link.input._data['database']
                if db not in foreground:
                    foreground[db] = []
                if link.input not in foreground[db]:
                    if verbose:
                        print(name + " not found.")
                    foreground[db].append(link.input)
                heap.append((link.input, amount))
        del heap[0]
        depth -= 1
    # Result formatting
    costs = pd.DataFrame({'Product': Expenses.keys(), 'Costs': Expenses.values()})
    costs.to_clipboard(index=False)
    if verbose: print("Costs copied to clipboard.")
    print("Total cost of inputs: €%.2f" % costs.Costs.sum())
    return costs, foreground

def added_value_db(Prices, db):
    """Compose a database of added value for all processes in a database. 
    Prices: dict with product prices (should match DB)
    db: bw2data.Database object 
    """
    #result = {}
    outfile = open("AddedValue.csv", 'w')
    for act in db:
        product = [p for p in act.production()][0]
        if product.output['reference product'] not in Prices:
            print("Price unknown for", act["name"])
            continue
        value = [product.amount * Prices[product.output['reference product']]]
        value += [ -link.amount * Prices[link.input['reference product']]
                    for link in act.technosphere()]
        # result[(act["code"], act["name"])] = sum(value)
        added_value = sum(value) / product.amount
        outfile.write('\t'.join([act["code"], act["name"], str(added_value)]))
        outfile.write('\n')
    outfile.close()
    #return result

def price_errors(Prices, db):
    """Report possible errors in `Prices` dict,
    by comparing the price of inputs with the price of the product.
    db: bw2data.Database object 
    """
    outfile = open("PriceErrors.csv", 'w')
    for act in db:
        product = [p for p in act.production()][0]
        prod_name = product.output['reference product']
        if prod_name not in Prices:
            print("Price unknown for", act["name"])
            continue
        prod = product.amount * Prices[prod_name]
        inputs = {link.input['reference product']:
                  link.amount * Prices[link.input['reference product']]
                  for link in act.technosphere()}
        if prod < 0.8*sum(inputs.values()): #or prod >= 2*sum(inputs.values())
            # print(prod_name, prod)
            for i in inputs:
                outfile.write('\t'.join([prod_name, i, str(inputs[i]), str(inputs[i]/prod])))
                outfile.write('\n')
    outfile.close()

def added_value_calc(av_file, lca):
    """Calculates how much money is made by all upstream processes
    in the supply chain of a product.
    `av_file`: path to CSV with added values.
    `lca`: bw2calc.LCA object, specifying the funtional flow.
    """
    # Read added value dataset
    av = pd.read_csv(av_file, sep='\t', encoding="ansi", names=["code", "name", "added_value"], index_col=0) #header=None,
    # rev_activity = {v: k for k, v in lca.activity_dict.items()}
    activities = [] #[k[1] for k in lca.activity_dict.keys()]
    regions = []
    # Collect info about activities
    for act in lca.activity_dict.keys(): #for i in range(len(rev_activity)):
        activities.append(act[1])
        activity = bd.get_activity(act)
        regions.append(activity.get('location'))
    # For new Brightway2 version:
    # activities = [k[1] for k in lca.dicts.activity.keys()]
    
    # Compose supply table 
    supply = pd.DataFrame({"code": activities, "amount": lca.supply_array, "region": regions})
    # Select nonzero entries
    supply = supply[supply.amount!=0]
    result = pd.merge(supply, av, 'left', on="code")
    result["added"] = result.amount * result.added_value
    return result.sort_values('added', ascending=False)

def find_inputs(functional_unit, fg_db):
    """Find all inputs from the background to produce `functional_unit`.
    `fg_db` is a Brightway database. Returns list of input quantities.
    """
    inputs = {}
    heap = [(functional_unit, 1)] # Starting point of graph traversal
    while len(heap) > 0:
        activity, demand = heap[0]
        for link in activity.technosphere():
            amount = link.amount * demand / [p for p in activity.production()][0].amount
            name = link.input['reference product']
            # Inputs in fg_db are considered foreground
            if link.input in fg_db:
                heap.append((link.input, amount))
            else:
                if name not in inputs:
                    inputs[name] = [amount, link.unit]
                else:
                    inputs[name][0] += amount
        del heap[0]
    return inputs

price_file = "C:/Users/nielenssvan/surfdrive/LCC/prices_ei38.csv"
Prices = pd.read_csv(price_file)
Prices = {Prices.name[p]: Prices.amount[p] for p in Prices.index}
added_value_db(Prices, bd.Database("cutoff38"))
price_errors(Prices, bd.Database("cutoff38"))

# Do LCC calculation 
funit = bd.Database{"x").search("item")[0]
costs, foreground = lcc(funit, Prices) #, verbose=True

# Find background inputs
import bw2data as bd
bd.projects.set_current("SUSMAGPRO")
my_db = bd.Database("LCIs_D7_20220420")
funit = my_db.search("Cutting")[0]
L = find_inputs(funit, my_db)

# Calculate LCA for a product
funit = bd.Database("cutoff38").search("zucchini")[1]
lca = bw2calc.LCA({funit: 1}, bd.methods.random())
lca.lci()
# Determine added values
av = added_value_calc("AddedValue.csv", lca)
contr = av.pivot_table('added', 'region', aggfunc='sum').sort_values('added')
contr["gain"] = av[av.added>0].pivot_table('added', 'region', aggfunc='sum')
contr["loss"] = av[av.added<0].pivot_table('added', 'region', aggfunc='sum')

-#TODO
    # Identify processes with large price-value gap.
    Run AV calculation, check input value/output price
    price_errors() function
    #`Calculated based on inputs`: check if still true, add margin.
    ...
    #Correct price mistakes: 
    hard coal, run-of-mine 70€/t
    titanium dioxide
    #Investigate strange products:
    barge production
    platinum group metal, extraction and refinery operations
    consumer electronics production, mobile device, smartphone
    liquid crystal display, unmounted, mobile device (=> price duplicates)
    converting vinasse to fertilizer needs subsidy (pricy input)
    
Approach
    About 1400 of 3324 products are Calculated based on inputs.
    Remove obvious mistakes
    Identify most important contributors
    Look up accurate price for those
