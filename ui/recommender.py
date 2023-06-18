class AprioriRecommentor:
    def __init__(self, data, min_support_val):
        self.data = data
        self.min_support_val =min_support_val
        #create association rule
        self.sorted_association_rules_in_market = self.create_Aprioli_ARL_rules()

    def create_apriori_matric_for_products(self):
        """
        This functions groups the data against its invoice number and stock code and then create a matrix between them.
        @params: data: DataFrame - Data to be transformed
        @return: A dataframe object with unstacked matrix
        """
        return self.data.groupby(['InvoiceNo', "StockCode"])['Quantity'].sum().unstack().fillna(0).applymap(lambda val: 1 if val > 0 else 0)


    #this function finds an item by its stock id
    def find_stock_by_id(self, stockCode):
        """
        This functions return details of a product from stockcode given
        @param : stockCode : A string representing the code of the stock
        @returns
            StockCode: a string represeting selected stock code
            product_desc : Description of the product selected

        """
        product_desc = self.data[self.data["StockCode"] == stockCode]["Description"].unique()
        return stockCode, product_desc[0]

    def create_Aprioli_ARL_rules(self):
        invoice_product_matrix = self.create_apriori_matric_for_products()
        # get apriori frequency for items
        apriori_freq_data = apriori(
            invoice_product_matrix, 
            min_support= self.min_support_val, 
            use_colnames=True)  
        association_rules_in_market = association_rules(
            apriori_freq_data, 
            metric="lift", 
            min_threshold=self.min_support_val)
        #sort these rules
        sorted_association_rules_in_market = association_rules_in_market.sort_values(['confidence', 'lift'], ascending =[False, False])

        return sorted_association_rules_in_market

    def recommend_product_to_user(self, prod_id, max_recommendent_items =10):
        # lets try recomment a user who has bought food with stockCode `prod_id`
        items_recommended = []
        # iterate through all antecendents
        for idx, product in enumerate(self.sorted_association_rules_in_market["antecedents"]):
            #since we saw antecent as tuple we need to get each item id
            for j in list(product):
                if str(j) == str(prod_id):
                    #lets get the id of current index
                    items_recommended.append(list(self.sorted_association_rules_in_market.iloc[idx]["consequents"])[0])
                    #remove duplicates using dictionary as key
                    items_recommended = list( dict.fromkeys(items_recommended))


        return items_recommended[:max_recommendent_items]


    def show_products_recommended_to_user(self,prod_id, max_recommendent_items=10):
        #check if product id is present
        if str(prod_id) in list(self.data["StockCode"].astype("str").unique()):
            #get the recommended list
            recommended_product_list = self.recommend_product_to_user(str(prod_id), max_recommendent_items)
            #check if there was any product recommended to the user i.e if list is empty
            if len(recommended_product_list) == 0:
                return {"Product_Code":prod_id,"data":[], "advice":"There was no any product that can be recommended to this user"}
            else:
                res = []
                for index in range(0, len(recommended_product_list)):
                    curr_product = self.find_stock_by_id(recommended_product_list[index])
                    res.append({
                        "Product_code": curr_product[0],
                        "Description": curr_product[1]
                    })
                
                return {"Product_Code":prod_id,"data":res, "advice":"We have the following products recommended for you"}

        else:
            return {"Product_Code":prod_id,"data":[], "advice":f"Code  {prod_id} was invalid as it is not in the stock"}

