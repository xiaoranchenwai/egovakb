interface datasetData {
  name: String
  desc: String
  documents?: Array<any>
  type?: String
  embedding_mode_id?: String | Array<String>
  question_model_id?: String
  create_default_app?: Boolean
  _submitData?: datasetData
}

export type { datasetData }
