from agents.rag_agent import create_agent



class QueryService:


    def __init__(self):

        self.agent = create_agent()



    async def ask(
            self,
            request
    ):


        customer_id = request.customer_id

        question = request.question



        #
        # Future PostgreSQL call
        #
        # customer_profile =
        # get_customer_profile(customer_id)
        #



        payload = {


            "customer_id":
            customer_id,


            "question":
            question

        }



        result = self.agent.invoke(
            payload
        )



        return {


            "status":
            "SUCCESS",


            "customer_id":
            customer_id,


            "response":
            result

        }