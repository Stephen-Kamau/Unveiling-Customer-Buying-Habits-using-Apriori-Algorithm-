import pickle
from recommender import AprioriRecommentor
import json


from flask import Flask, flash, request, redirect, render_template,url_for


app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def index():
    #load the model
    with open("./recommender_model.pkl", "rb") as model_object:
        model = pickle.load(model_object)
        model_object.close()
    #get random ids to show the user samples
    sample_product_ids =[]
    for prod_ids in model.sorted_association_rules_in_market["antecedents"]:
        sample_product_ids +=list(dict.fromkeys(prod_ids).keys())
        
    import random
    random_ids = " ,".join(str(x) for x in random.sample(sample_product_ids, 10))
    #check if request is post
    if request.method == 'POST':
        #extract the code typed
        product_code_entered = request.form['product_code']
        res = model.show_products_recommended_to_user(product_code_entered)
        if len(res['data']) ==0:
            return render_template("./res.html", result=None, result_id = None, random_ids_codes = random_ids)
        
        
        res_data = [list(da.values()) for da in res['data']]
        res_id = res['Product_Code']

        return render_template("./res.html", result=res_data, result_id = res_id, random_ids_codes = random_ids)

    else:
        return render_template("./res.html", result=None, result_id = 1, random_ids_codes = random_ids)

if __name__ == "__main__":
    app.run()