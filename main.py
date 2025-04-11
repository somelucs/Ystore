try:
    import requests
    import time
    from flask import Flask,render_template,request,jsonify,make_response,url_for,redirect
    import json
    from datetime import datetime
    import pytz
    import pandas as pd
    import base64
    from solders.signature import Signature
    from solders.pubkey import Pubkey
    from solders.message import Message
    from solders.hash import Hash
    from solders.signature import Signature
    import os
    import random
    import string

    app=Flask(__name__)

    url = "https://api.devnet.solana.com"
    headers = {
    "Content-Type": "application/json"
    }
    def get_signatures(address, limit=1):
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": limit}]
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json().get("result", [])

    def check_transaction_status(signature,nm, max_attempts=1, delay=5):
        RPC_URL='https://api.devnet.solana.com'
        headers = {"Content-Type": "application/json"}

        for attempt in range(max_attempts):
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [signature, {"encoding": "json", "commitment": "finalized"}]
            }

            response = requests.post(RPC_URL, json=payload, headers=headers)
            result = response.json().get("result")

            if result:
                print("\n✅h\n")
                block_time = result.get("blockTime")
                slot = result.get("slot")
                post_balances = result.get("meta", {}).get("postBalances")
                transaction_accounts = result["transaction"]["message"]["accountKeys"][0]
                pre_balances = result.get("meta", {}).get("preBalances")

                if pre_balances and post_balances:

                    sol_transferred = (pre_balances[0] - post_balances[0]) / 1_000_000_000
                    
                    if str(transaction_accounts)==str(request.cookies.get('user')) and 1.4>=(sol_transferred)/float(request.args.get('val'))>=1:
                       
                        return render_template('sucesso.html',mn=sol_transferred)
                    else:
                        return '<script>alert("Payment not found");window.location.href="/reg"</script>'
               

    @app.route('/')
    def index():
        return render_template('menu.html')
    @app.route('/cad')
    def cadastro():       
        return render_template('cadastro.html')
        
    @app.route('/pags')
    def pagamentos():
        qry=request.args.get('q')
        val=request.args.get('v')
        url='solana:89BBgM9DZSgMUSkc3zptNzXw7Zt7tjgJyUVx4RrkXBzW?amount='+str(val).replace('Preço:','')+'&spl-token=SOL&network=devnet'
        return render_template('pagamento.html',link=url,valor=str(val).replace('Preço:',''),name=qry)
    @app.route('/trns')
    def transacao():
        url = "https://api.devnet.solana.com"  
        headers = {
            "Content-Type": "application/json"
        }

        address = "89BBgM9DZSgMUSkc3zptNzXw7Zt7tjgJyUVx4RrkXBzW"

        def get_signatures(address, limit=10):
            data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [address, {"limit": limit}]
            }

            response = requests.post(url, json=data, headers=headers)
            return response.json().get("result", [])

        def get_transaction(signature):
            data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [signature]
            }

            response = requests.post(url, json=data, headers=headers)
            return response.json().get("result", {})

        def process_transactions(address):
            signatures = get_signatures(address)

            if not signatures:
                print("Transaction not found")
                return

            for signature in signatures:
                print(f"Processing: {signature['signature']}")
                return check_transaction_status(signature['signature'],request.args.get('nm'))

        solana_address = "89BBgM9DZSgMUSkc3zptNzXw7Zt7tjgJyUVx4RrkXBzW"
        return process_transactions(solana_address)
        
        

    @app.route('/reg')
    def registro():
        def rgs():
            mtx=[]
            with open("imgs.json", "r") as arquivo2:
                dadosI = json.load(arquivo2)
            mtxI=[]
            for i in range(len(dadosI)):
                mtxI.append(dadosI[str(i+1)])

            with open("regs.json", "r") as arquivo:
                dados = json.load(arquivo)
                if dados!={}:
                    prods = list(dados.keys())
                    val = list(dados.values())
                    for i in range(len(val)):
                        mtx.append(['Produto:'+prods[i],'Preço:'+val[i]])
            return {"regs":mtx,"imgs":mtxI}
           

        
            
         
        return render_template('prods.html',**rgs(),req=str(request.cookies.get('usr')))
    
    @app.route('/psq',methods=['POST'])
    def pesq():
        if request.args.get('psq')!=None:
            return redirect(url_for('src',q=str(request.form['psq']).replace(' ','E')))
    @app.route('/src')
    def src():
        qry=request.args.get('q')
        mtxn=[]
        mQry=qry.split('E')
        for z in range(len(mQry)):
            with open("regs.json", "r") as arquivo:
                sQry=mQry[z]
                dados = json.load(arquivo)
                prods = list(dados.keys())
                val = list(dados.values())
                for i in range(len(prods)):
                    strProds=prods[i].split(' ')
                    for w in range(len(strProds)):
                        if strProds[w]==sQry:
                            mtxn.append(i)
            def rgs():
                mtx=[]
                with open("imgs.json", "r") as arquivo2:
                    dadosI = json.load(arquivo2)
                mtxI=[]
                

                with open("regs.json", "r") as arquivo:
                    dados = json.load(arquivo)
                    if dados!={}:
                        prods = list(dados.keys())
                        val = list(dados.values())
                        for i in range(len(val)):
                            for w in range(len(mtxn)):
                                if i==mtxn[w]:
                                    mtx.append(['Produto:'+prods[i],'Preço:'+val[i]])
                                    mtxI.append(dadosI[str(i+1)])
                return {"regs":mtx,"imgs":mtxI}
        return render_template('prods.html',**rgs(),req=str(request.cookies.get('user')))


    @app.route('/create', methods=['POST'])
    def create():
        if request.referrer!='/reg':
            prod=request.form['prod']
            val=request.form['val']
            with open("regs.json", "r") as arquivo:
                dados = json.load(arquivo)
            with open("imgs.json", "r") as arquivo2:
                dadosI = json.load(arquivo2)
            dados[prod]=str(val)
            file = request.files["img"]
            if file.filename!="":
                file.save("static/"+file.filename)
                dadosI[str(len(dadosI)+1)]=file.filename
            else:
                dadosI[str(len(dadosI)+1)]="N"
            mtxI=[]
            for i in range(len(dadosI)):
                mtxI.append(dadosI[str(len(dadosI))])

        
            with open("regs.json", "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, indent=4, ensure_ascii=False)
            with open("imgs.json", "w", encoding="utf-8") as arquivo2:
                json.dump(dadosI, arquivo2, indent=4, ensure_ascii=False)
            def rgs():
                mtx=[]

                with open("regs.json", "r") as arquivo:
                    dados2 = json.load(arquivo)
                    if dados2!={}:
                        prods = list(dados2.keys())
                        val = list(dados2.values())
                        for i in range(len(val)):
                            mtx.append(['Produto:'+prods[i],'Preço:'+val[i]])
                return {"regs":mtx}

        return render_template('prods.html',**rgs(),imgs=mtxI,req=str(request.cookies.get('user')))

    challenges = {}
    

    def generate_challenge():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    @app.route("/get_challenge", methods=["POST","GET"])
    def get_challenge():
       
        data = request.get_json()
        pubkey = data.get("pubkey")
        ck=json.dumps(pubkey)
        if pubkey:
            resp = make_response(url_for('verify_signature'))
            resp.set_cookie('usr',ck,max_age=60*60*24)
        if not pubkey:
            return jsonify({"error": "Pub key not found"}), 400

        challenge = generate_challenge()
        challenges[pubkey] = challenge  

        return jsonify({"challenge": challenge}), resp.get_data(as_text=True)

    @app.route("/verify_signature", methods=["POST"])
    def verify_signature():
        if request.referrer=='/verif':
            pass

        data = request.get_json()
        pubkey = data.get("pubkey")
        signature_b64 = data.get("signature")

        if not pubkey or not signature_b64:
            print('erro')
            return jsonify({"error": "Imcomplete data"}), 400

        challenge = challenges.get(pubkey)

        if not challenge:
            print('erro')
            return jsonify({"error": "Challenge not found"}), 400

        try:

            pubkey_obj = Pubkey.from_string(pubkey)
            signature_bytes = base64.b64decode(signature_b64)
            signature_obj = Signature.from_bytes(signature_bytes)

            is_valid = signature_obj.verify(pubkey_obj, challenge.encode())


            if is_valid:
                return jsonify({"status": "success", "url1": "/reg?"+str(pubkey_obj),"url2":'/pags'})
        
        


            else:
                print('erro')
                return jsonify({"error": "Invalid signature"}), 401
        except Exception as e:
            print(f'erro:{e}')

    @app.route("/verify_signature2", methods=["POST"])
    def verify_signature2():
        data = request.get_json()
        pubkey = data.get("pubkey")
        signature_b64 = data.get("signature")

        if not pubkey or not signature_b64:
            print('erro')
            return jsonify({"error": "Imcomplete data"}), 400

        challenge = challenges.get(pubkey)

        if not challenge:
            print('erro')
            return jsonify({"error": "Challenge not found"}), 400

        try:
            pubkey_obj = Pubkey.from_string(pubkey)
            signature_bytes = base64.b64decode(signature_b64)
            signature_obj = Signature.from_bytes(signature_bytes)

            is_valid = signature_obj.verify(pubkey_obj, challenge.encode())


            if is_valid:
                return jsonify({"status": "success","url1": "/rgs","url2":'/pags'}), 200
                


            else:
                print('erro')
                return jsonify({"error": "Invalid signature"}), 401

        except Exception as e:
            print(f'erro:{e}')
        finally:
            print('Press enter to exit ')


    if __name__ == '__main__':
        app.run(debug=True,port=3000)
except Exception as e:
    print(f'erro:{e}')
finally:
    print('Press enter to exit ')
