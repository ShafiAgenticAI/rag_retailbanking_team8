from app.agents.rag_agent import call_agent


class QueryService:

    @staticmethod
    def process_query(request):

        response = call_agent(
            question=request.question, customer_details=request.input_json
        )

        return {
            "answer": response.output_response,
            "sources": [
                {
                    "file_name": chunk.metadata.file_name,
                    "page_number": chunk.metadata.page_number,
                    "snippet": chunk.content,
                    "file_extension": chunk.metadata.file_extension,
                }
                for chunk in response.retrieved_chunks
            ],
        }
