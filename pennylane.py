# Script Calcul de TVA API Pennylane
# Nicolas Bellet @ pavillonnoir
# ahcarrement.fr - 2023

import requests
from tabulate import tabulate

annee = int(input("Année ? (YYYY)"))
mois = int(input("Mois ? (MM)"))

digitmois = ("{:02d}".format(mois))
add = int(1)
suiv = ("{:02d}".format(int(digitmois) + add))
headers = {
    "accept": "application/json",
    "authorization": "Bearer YOUR-PENNYLANE-API-KEY"
}

def get_data_facturation():
    response = requests.get("https://app.pennylane.com/api/external/v1/customer_invoices?per_page=200", headers=headers)
    return response.json()['invoices']

def get_data_paiements():
    response = requests.get("https://app.pennylane.com/api/external/v1/supplier_invoices?per_page=200", headers=headers)
    return response.json()['invoices']

facturation = get_data_facturation()
paiement = get_data_paiements()

filtre_facturation = [item for item in facturation if len(item['matched_transactions']) != 0 and item['matched_transactions'][0]['date'] >= str(annee) + '-' + digitmois + '-01' and item['matched_transactions'][0]['date'] < str(annee) + '-' + suiv + '-01']
filtre_paiement = [item for item in paiement if len(item['matched_transactions']) != 0 and item['matched_transactions'][0]['date'] >= str(annee) + '-' + digitmois + '-01' and item['matched_transactions'][0]['date'] < str(annee) + '-' + suiv + '-01']

def simplifier_facturation(item):
    return {
        'Date': item['matched_transactions'][0]['date'],
        'Nom': item['filename'],
        'HT': item['currency_amount_before_tax'],
        'TVA': item['currency_tax'],
        'TTC': item['amount']
    }

def simplifier_paiement(item):
    return {
        'Date': item['matched_transactions'][0]['date'],
        'Nom': item['label'],
        'HT': float(item['matched_transactions'][0]['amount']) * -1 - float(item['currency_tax']),
        'TVA': item['currency_tax'],
        'TTC': float(item['matched_transactions'][0]['amount']) * -1
    }

data_facturation = map(simplifier_facturation, filtre_facturation)
data_paiements = map(simplifier_paiement, filtre_paiement)

tri_facturation = sorted(data_facturation, key=lambda item: item['Date'])
tri_paiement = sorted(data_paiements, key=lambda item: item['Date'])

#Calcul sommes
somme_fact_HT = sum((float(c['HT'])) for c in tri_facturation)
somme_fact_TVA = sum((float(c['TVA'])) for c in tri_facturation)
somme_fact_TTC = sum((float(c['TTC'])) for c in tri_facturation)
somme_pai_HT = sum((float(c['HT'])) for c in tri_paiement)
somme_pai_TVA = sum((float(c['TVA'])) for c in tri_paiement)
somme_pai_TTC = sum((float(c['TTC'])) for c in tri_paiement)


# Imprimer le résultat final
print("\n\nENCAISSEMENTS :")
print(tabulate(tri_facturation, headers="keys", tablefmt="simple_outline"))
print("\nTotal encaissé HT : ", "{:.0f}".format(somme_fact_HT), " ( TVA à payer : ", "{:.0f}".format(somme_fact_TVA), ")")
print("\n\nDECAISSEMENTS :")
print(tabulate(tri_paiement, headers="keys", tablefmt="simple_outline"))
print("\nTotal paiements HT : ", "{:.0f}".format(somme_pai_HT), " - TVA à récupérer : ", "{:.0f}".format(somme_pai_TVA))
print("\nDifférence HT : ", "{:.0f}".format(somme_fact_HT - somme_pai_HT), " - DECLARATION TVA : ", "{:.0f}".format(somme_fact_TVA - somme_pai_TVA))
