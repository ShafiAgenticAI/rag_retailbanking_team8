import os
import uuid
import shutil


from ingestion.ingestion import ingest_document



class UploadService:


    DATA_FOLDER = "data"



    async def upload(
            self,
            file,
            customer_id
    ):


        os.makedirs(
            self.DATA_FOLDER,
            exist_ok=True
        )


        document_id = str(uuid.uuid4())


        filename = (
            document_id 
            + "_"
            + file.filename
        )


        file_path = os.path.join(
            self.DATA_FOLDER,
            filename
        )


        # Save file

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        #
        # Future PostgreSQL call
        #
        # save document metadata
        #
        # document_id
        # customer_id
        # filename
        # upload_date
        #


        ingestion_result = ingest_document(
            file_path,
            customer_id,
            document_id
        )


        return {

            "status":
            "SUCCESS",

            "document_id":
            document_id,

            "file":
            filename,

            "ingestion":
            ingestion_result
        }