import ApiService from "./api";

export class NotebookService {
    getNotebooks(){
        return ApiService.get("/notebookjobs")
    }
}
