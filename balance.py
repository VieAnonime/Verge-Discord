import discord, json, requests, pymysql.cursors
from discord.ext import commands

def rpcdat(method,params,port):
    try:
        rpcdata = json.dumps({
            "jsonrpc": 1.0,
            "id":"rpctest",
            "method": str(method),
            "params": params,
            "port": port
            })
        req = requests.get('http://127.0.0.1:'+port, data=rpcdata, auth=('user', 'pass'), timeout=8)
        return req.json()['result']
    except Exception as e:
        return "Error: "+str(e)

class balance:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def balance(self, ctx):
        author = ctx.message.author

        port =  "11311"
        params = str(ctx.message.author)
        user_wallet_bal = rpcdat('getbalance',[params],port)

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='netcoin')
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""SELECT balance, user
                            FROM db
                            WHERE user
                            LIKE %s
                            """, str(author))
            result_set = cursor.fetchone()

            if str(float(result_set['balance'])) == str(user_wallet_bal):
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="User", value=result_set['user'])
                embed.add_field(name="Balance (NET)", value=result_set['balance'])
                embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

                try:
                    await self.bot.say(embed=embed)
                except discord.HTTPException:
                    await self.bot.say("I need the `Embed links` permission "
                                    "to send this")
            else:
                print(str(float(result_set['balance']))+" "+str(user_wallet_bal))
                if float(result_set['balance']) > float(user_wallet_bal) or float(result_set['balance']) < float(user_wallet_bal):
                    await self.bot.say("DB: Wallet balance does not match db balance")

        except Exception as e:
            print(e)
            try:
                cursor.execute("""INSERT INTO db(user,balance) VALUES(%s,%s)""", (str(author), '0'))
                connection.commit()

                cursor.execute("""SELECT balance, user
                                FROM db
                                WHERE user
                                LIKE %s
                                """, str(author))
                result_set = cursor.fetchone()
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="User", value=result_set['user'])
                embed.add_field(name="Balance (NET)", value=result_set['balance'])
                embed.set_footer(text="Sponsored by altcointrain.com")

                try:
                    await self.bot.say(embed=embed)
                except discord.HTTPException:
                    await self.bot.say("I need the `Embed links` permission to send this")

            except Exception as ex:
                print(ex)
def setup(bot):
    bot.add_cog(balance(bot))
