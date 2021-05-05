import React from "react";
import {
  Button,
  Alert,
  Form,
  Table,
  Breadcrumb,
  Spin,
  Row,
  Col,
  Radio,
  notification,
  Modal,
  Input
} from "antd";
import _ from "lodash";
// import ErrorBoundary from "components/layout/ErrorBoundary";

import AceEditor from "react-ace";
import RSelect from "react-select";

import notebookService from "services/notebooks.js";

import "ace-builds/src-noconflict/mode-json";
import "ace-builds/src-noconflict/theme-github";

const datasetDetailsConst = {"dremioSchema":[{"columnName":"OrderTS","dataType":"TIMESTAMP"},{"columnName":"OPK","dataType":"DECIMAL"},{"columnName":"OrderStatus","dataType":"STRING"},{"columnName":"OrderEntries","dataType":"NONE"},{"columnName":"Consignments","dataType":"NONE"},{"columnName":"FirstAllocMin","dataType":"NONE"},{"columnName":"LastAllocMin","dataType":"NONE"},{"columnName":"FirstToLastAllocMin","dataType":"NONE"},{"columnName":"NonReturnConsignments","dataType":"NONE"},{"columnName":"LastNonReturnAllocMin","dataType":"NONE"}],"druidIngestionSpec":"{\"type\": \"index\", \"spec\": {\"dataSchema\": {\"dataSource\": \"ALLOCATION\", \"timestampSpec\": {\"column\": \"OrderTS\", \"format\": \"millis\", \"missingValue\": null}, \"dimensionsSpec\": {\"dimensions\": [{\"type\": \"string\", \"name\": \"OrderStatus\", \"multiValueHandling\": \"SORTED_ARRAY\", \"createBitmapIndex\": true}]}, \"metricsSpec\": [{\"type\": \"count\", \"name\": \"count\"}, {\"type\": \"doubleSum\", \"name\": \"OPK\", \"fieldName\": \"OPK\", \"expression\": null}], \"granularitySpec\": {\"type\": \"uniform\", \"segmentGranularity\": \"MONTH\", \"queryGranularity\": \"MINUTE\", \"rollup\": true, \"intervals\": null}, \"transformSpec\": {\"filter\": null, \"transforms\": []}}, \"ioConfig\": {\"type\": \"index\", \"inputSource\": {\"type\": \"s3\", \"uris\": null, \"prefixes\": [\"s3://ssl-cuebook/druid-cubes/ALLOCATION/\"], \"objects\": null}, \"inputFormat\": {\"type\": \"parquet\", \"flattenSpec\": {\"useFieldDiscovery\": true, \"fields\": []}, \"binaryAsString\": false}, \"appendToExisting\": false}, \"tuningConfig\": {\"type\": \"index_parallel\", \"maxRowsPerSegment\": 5000000, \"maxRowsInMemory\": 1000000, \"maxBytesInMemory\": 0, \"maxTotalRows\": null, \"numShards\": null, \"splitHintSpec\": null, \"partitionsSpec\": {\"type\": \"dynamic\", \"maxRowsPerSegment\": 5000000, \"maxTotalRows\": null}, \"indexSpec\": {\"bitmap\": {\"type\": \"concise\"}, \"dimensionCompression\": \"lz4\", \"metricCompression\": \"lz4\", \"longEncoding\": \"longs\"}, \"indexSpecForIntermediatePersists\": {\"bitmap\": {\"type\": \"concise\"}, \"dimensionCompression\": \"lz4\", \"metricCompression\": \"lz4\", \"longEncoding\": \"longs\"}, \"maxPendingPersists\": 0, \"forceGuaranteedRollup\": false, \"reportParseExceptions\": false, \"pushTimeout\": 0, \"segmentWriteOutMediumFactory\": null, \"maxNumConcurrentSubTasks\": 1, \"maxRetry\": 3, \"taskStatusCheckPeriodMs\": 1000, \"chatHandlerTimeout\": \"PT10S\", \"chatHandlerNumRetries\": 5, \"maxNumSegmentsToMerge\": 100, \"totalNumMergeTasks\": 10, \"logParseExceptions\": false, \"maxParseExceptions\": 2147483647, \"maxSavedParseExceptions\": 0, \"buildV9Directly\": true, \"partitionDimensions\": []}}, \"context\": {\"forceTimeChunkLock\": true}, \"dataSource\": \"ALLOCATION\"}","isPublishedToDruid":false,"refreshSchedule":"0 35 5 * * ? *","isScheduleEnabled":false}

class DatasetSelector extends React.Component {
  DATATYPE_TO_MEASURE_MAP = new Map()
    .set("double", "doubleSum")
    .set("long", "longSum");

  constructor() {
    super();
    this.state = {
      spec: null,
      datasetLocation: null,
      datasourceName: null,
      datasetDetails: {},
      visible: false,
      schemaVerified: false
    };
  }

  showModal = () => {
    this.setState({ ...this.state, visible: true });
  };

  handleCancel = e => {
    this.setState({ ...this.state, visible: false });
  };

  handleDatasetChange = e => {
    this.setState({datasetLocation: e.target.value, datasetDetails: {}, schemaVerified: false, spec: null})
    this.props.onChange(undefined)
  }

  fetchSchema = () => {
    let payload = {
        datasourceName: this.state.datasourceName,
        datasetLocation: this.state.datasetLocation
    } 
    let newDatasetDetails = notebookService.getDatasetDetails(payload)
    this.setState({datasetDetails: newDatasetDetails})
  }

  clearSchema = () => {
    this.setState({datasetDetails: {}, schemaVerified: false, spec: null})
    this.props.onChange(undefined)
  }

  getDruidDataType = dremioDataType => {
    dremioDataType = dremioDataType.toUpperCase();

    if (["ENUM", "STRING", "UUID", "NONE"].includes(dremioDataType))
      return "string";
    if (["DECIMAL"].includes(dremioDataType))
      return "double";
    if (["INT"].includes(dremioDataType)) return "long";
    if (["TIME", "TIMESTAMP", "DATE"].includes(dremioDataType)) return "long";
    else return "";
  };

  getDimensionsAndMeasuresTable = (
    druidIngestionSpec,
    datasetDetails,
    isDatasetPublished
  ) => {
    if (
      _.isNil(druidIngestionSpec) ||
      _.isNil(JSON.parse(druidIngestionSpec).spec)
    )
      return;

    if (_.isNil(datasetDetails) || _.isNil(JSON.parse(druidIngestionSpec).spec))
      return;

    let isConfigUpdated = false;
    const parsedJSONSpec = JSON.parse(druidIngestionSpec).spec;
    let dimensions = parsedJSONSpec.dataSchema.dimensionsSpec.dimensions;
    const measures = parsedJSONSpec.dataSchema.metricsSpec;
    const timestampColumn = parsedJSONSpec.dataSchema.timestampSpec.column;

    const dimensionsSet = new Set(dimensions.map(e => e.name));
    const measuresSet = new Set(measures.map(e => e.fieldName));

    let dremioSchema = datasetDetails.dremioSchema;

    let mappedColumns = dremioSchema.map(e => {
      let columnName = e.columnName;
      let dremioDataType = e.dataType;

      let updatedRow = false;
      let columnType = "dimension";
      if (dimensionsSet.has(columnName)) {
        columnType = "dimension";
      } else if (measuresSet.has(columnName)) {
        columnType = "measure";
      } else if (columnName === timestampColumn) {
        columnType = "timestamp";
      } else {
        // it means the column is present in dremio spec but not in druid spec so add it.
        // any logic landing here should have the field added to the spec
        // let ob1 = {
        //   "type": "string",
        //   "name": columnName,
        //   "multiValueHandling": "SORTED_ARRAY",
        //   "createdBitmapIndex": true
        // }
        // dimensions.add(ob1);
        isConfigUpdated = true;
        // dremioDataType = "STRING";
      }

      // any entry that is not there in the dremio spec needs to be removed from the current druid spec

      return {
        columnName: columnName,
        columnType: columnType,
        dremioDataType: dremioDataType,
        druidDataType: this.getDruidDataType(dremioDataType),
        isUpdatedRow: updatedRow
      };
    });

    let isSchemaDifferent = false;

    if (isDatasetPublished) {
      if (mappedColumns.length !== measuresSet.size + dimensionsSet.size) {
        // mappedColumns = measures + dimensions + 1 (timestamp) - 1 (count dimension always)
        isSchemaDifferent = true;
      }
    }
    return {
      mappedColumns: mappedColumns,
      isSchemaUpdated: isSchemaDifferent || isConfigUpdated
    };
  };

  verifySchema = druidIngestionSpec => {
    const { spec } = this.state;
    let druidSpec = spec;

    if (_.isNil(spec)) {
      druidSpec = druidIngestionSpec;
    }

    const parsedJSONSpec = JSON.parse(druidSpec);
    const timestampColumn = parsedJSONSpec.spec.dataSchema.timestampSpec;

    if (_.isNil(timestampColumn.column)) {
      notification.warning({
        message: "Select Timestamp column",
        description:
          "Timestamp column is mandatory. Please select a timestamp column."
      });
      this.clearSchema()
      return;
    }
    this.setState({schemaVerified: true})
    this.props.onChange({datasourceName: this.state.datasourceName, datasetLocation: this.state.datasetLocation})
  };

  onChangeDruidDataType = (newValues, record, druidIngestionSpec) => {
    // now corresponding to this new value - update the druid ingestion spec.
    // this method is called when the user updates the datatype for e.g - from string to float

    const columnName = record["columnName"];
    const columnType = record["columnType"];
    const newDataType = newValues.value.toUpperCase();

    const parsedJSONSpec = JSON.parse(druidIngestionSpec);
    const dimensions = parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions;
    const measures = parsedJSONSpec.spec.dataSchema.metricsSpec;

    if (columnType.toUpperCase() === "MEASURE") {
      let measureObject = measures.filter(e => e.fieldName === columnName)[0];
      if (["INT", "LONG", "DOUBLE"].includes(newDataType)) {
        //DATATYPE_TO_MEASURE_MAP.get(newDataType.toUpperCase())
        measureObject["type"] = newDataType.toLowerCase() + "Sum";
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      } else {
        notification.warning({
          message: "Operation not allowed",
          description:
            "Cannot assign " +
            newDataType +
            " to a measure. Please select a numeric data type or mark this column as a dimension."
        });
      }
    } else if (columnType.toUpperCase() === "DIMENSION") {
      let dimensionObject = dimensions.filter(e => e.name === columnName)[0];
      if (["TIMESTAMP", "STRING", "LONG", "DOUBLE"].includes(newDataType)) {
        // time should be stored as Long internally . Dremio will store time in long format
        if (newDataType === "TIMESTAMP") dimensionObject["type"] = "long";
        else dimensionObject["type"] = newDataType.toLowerCase();
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      } else {
        notification.warning({
          message: "Operation not allowed",
          description: "Cannot assign " + newDataType
        });
      }
    }
    this.setState({schemaVerified: false})
    this.props.onChange(undefined)
  };

  onChangeDruidColumnType = (event, record, druidIngestionSpec) => {
    // as the user switches between a measure, dimension or timestamp

    const columnName = record["columnName"];
    const newColumnType = event.target.value;

    const parsedJSONSpec = JSON.parse(druidIngestionSpec);
    const dimensions = parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions;
    const measures = parsedJSONSpec.spec.dataSchema.metricsSpec;
    const timestampColumn = parsedJSONSpec.spec.dataSchema.timestampSpec;

    let selectedDimensions = dimensions.filter(e => e.name === columnName);
    let measureObject = measures.filter(e => e.fieldName === columnName);

    if (newColumnType.toUpperCase() === "MEASURE") {
      // find the entry from dimension or timestamp - remove it from there and add it to dimension
      // new schema should follow the representation

      if (selectedDimensions.length > 0) {
        let selectedDimensionDataType = selectedDimensions[0].type;

        if (
          !(
            selectedDimensionDataType.toUpperCase() === "LONG" ||
            selectedDimensionDataType.toUpperCase() === "DOUBLE"
          )
        ) {
          notification.warning({
            message: "Invalid Data Type",
            description:
              "Columns with only Long or Double Data Type can be used as measures."
          });
          return;
        }

        let newMeasureObject = {
          type: selectedDimensionDataType + "Sum",
          name: columnName,
          fieldName: columnName,
          expression: null
        };
        measures.push(newMeasureObject);
        parsedJSONSpec.spec.dataSchema.metricsSpec = measures;

        let newDimensions = dimensions.filter(e => e.name !== columnName);
        parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = newDimensions;
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      } else if (timestampColumn.column === columnName) {
        notification.warning({
          message: "Important!",
          description:
            "It is mandatory to have a timestamp column. Please mark another column as timestamp column. Converting this column to a measure."
        });

        let newMeasureObject = {
          type: "longSum",
          name: columnName,
          fieldName: columnName,
          expression: null
        };

        measures.push(newMeasureObject);
        parsedJSONSpec.spec.dataSchema.timestampSpec = {};
        parsedJSONSpec.spec.dataSchema.metricsSpec = measures;
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      }
    } else if (newColumnType.toUpperCase() === "DIMENSION") {
      // find the entry from measure or timestamp and move it to dimension
      if (measureObject.length > 0) {
        let newDimensionObject = {
          type: measureObject[0].type.replace("Sum", ""),
          name: columnName,
          multiValueHandling: "SORTED_ARRAY",
          createBitmapIndex: true
        };
        let newMeasures = measures.filter(e => e.fieldName !== columnName);
        dimensions.push(newDimensionObject);
        parsedJSONSpec.spec.dataSchema.metricsSpec = newMeasures;
        parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = dimensions;
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      } else if (timestampColumn.column === columnName) {
        notification.warning({
          message: "Important!",
          description:
            "It is mandatory to have a timestamp column. Please mark another column as timestamp column. Converting this column to a dimension."
        });

        let newDimensionObject = {
          type: "long",
          name: columnName,
          multiValueHandling: "SORTED_ARRAY",
          createBitmapIndex: true
        };
        dimensions.push(newDimensionObject);
        parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = dimensions;
        parsedJSONSpec.spec.dataSchema.timestampSpec = {};
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      }
    } else if (newColumnType.toUpperCase() === "TIMESTAMP") {
      // find the entry from measure or dimension and move it to timestamp column
      // there can be only 1 timestamp column - so take action accordingly.
      // write down all these validations

      // here means converting a measure to a timestamp
      if (measureObject.length > 0) {
        let measureObjectDataType = measureObject[0].type.replace("Sum", "");
        if (
          measureObjectDataType.toUpperCase() !== "LONG" &&
          measureObjectDataType.toUpperCase() !== "TIMESTAMP"
        ) {
          notification.warning({
            message: "Invalid Data Type",
            description:
              "The timestamp datatype can only be long. The data in the fields should be the time in millis stored in a Long variable."
          });
          return;
        }
        let newTimestampObject = {
          column: columnName,
          format: "millis",
          missingValue: null
        };

        // Convert existing timestamp column to a dimension

        if (!_.isNil(timestampColumn)) {
          let newDimensionObject = {
            type: "long",
            name: timestampColumn.column,
            multiValueHandling: "SORTED_ARRAY",
            createBitmapIndex: true
          };

          // convert existing timestamp object
          dimensions.push(newDimensionObject);
        }

        // remove the selected column from the measures list
        let newMeasures = measures.filter(e => e.fieldName !== columnName);
        parsedJSONSpec.spec.dataSchema.metricsSpec = newMeasures;

        // assign the same column to the timestamp list
        parsedJSONSpec.spec.dataSchema.timestampSpec = newTimestampObject;

        // convert the existing timestamp column to dimensions and push it to the
        // dimensions list
        parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = dimensions;
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      } else if (selectedDimensions.length > 0) {
        let selectedDimensionDataType = selectedDimensions[0].type;

        if (
          selectedDimensionDataType.toUpperCase() !== "LONG" &&
          selectedDimensionDataType.toUpperCase() !== "TIMESTAMP"
        ) {
          notification.warning({
            message: "Invalid Data Type",
            description:
              "The timestamp datatype can only be long. The data in the fields should be the time in millis stored in a Long variable."
          });
          return;
        }

        let newTimestampObject = {
          column: columnName,
          format: "millis",
          missingValue: null
        };

        let newDimensions = dimensions.filter(e => e.name !== columnName);
        if (!_.isNil(timestampColumn) && !_.isNil(timestampColumn.column)) {
          let newDimensionObject = {
            type: "long",
            name: timestampColumn.column,
            multiValueHandling: "SORTED_ARRAY",
            createBitmapIndex: true
          };

          newDimensions.push(newDimensionObject);
        }
        parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = newDimensions;
        parsedJSONSpec.spec.dataSchema.timestampSpec = newTimestampObject;
        this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
      }
    }
    this.setState({schemaVerified: false})
    this.props.onChange(undefined)
  };

  updateCurrentDruidIngestionSpec = (druidIngestionSpec, datasetDetails) => {
    // this method is to update the existing druid ingestion spec
    // if the column has been removed from the dremio schema but is present in the druid spec, remove it.
    // if the column has been added to dremio spec and it is not present in the druid spec, add it.
    if (
      _.isNil(druidIngestionSpec) ||
      _.isNil(JSON.parse(druidIngestionSpec).spec)
    )
      return;

    if (_.isNil(datasetDetails) || _.isNil(JSON.parse(druidIngestionSpec).spec))
      return;

    // Removing the columns from Druid spec which are not present in Dremio spec
    const parsedJSONSpec = JSON.parse(druidIngestionSpec);
    let dimensions = parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions;
    let measures = parsedJSONSpec.spec.dataSchema.metricsSpec;
    const timestampColumn = parsedJSONSpec.spec.dataSchema.timestampSpec.column;

    let dremioSchema = datasetDetails.dremioSchema;

    const dremioColumnsSet = new Set(dremioSchema.map(e => e.columnName));

    if (!dremioColumnsSet.has(timestampColumn)) {
      // remove if timestamp column is absent
      parsedJSONSpec.spec.dataSchema.timestampSpec.column = null;
    }

    dimensions = dimensions.filter(e => dremioColumnsSet.has(e.name));
    measures = measures.filter(
      e => dremioColumnsSet.has(e.fieldName) || e.name.toUpperCase() === "COUNT"
    );

    parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = dimensions;
    parsedJSONSpec.spec.dataSchema.metricsSpec = measures;

    // If the column has been added to Dremio spec and it is not present in the Druid spec, add it.

    const dimensionsSet = new Set(dimensions.map(e => e.name));
    const measuresSet = new Set(measures.map(e => e.fieldName));

    let newDims = [];
    let mappedColumns = dremioSchema.forEach(e => {
      let columnName = e.columnName;
      let dremioDataType = e.dataType;

      let updatedRow = false;
      let columnType = "dimension";
      if (dimensionsSet.has(columnName)) {
        columnType = "dimension";
      } else if (measuresSet.has(columnName)) {
        columnType = "measure";
      } else if (columnName === timestampColumn) {
        columnType = "timestamp";
      } else {
        //it means the column is present in dremio spec but not in druid spec so add it.
        //any logic landing here should have the field added to the spec
        let ob1 = {
          type: "string",
          name: columnName,
          multiValueHandling: "SORTED_ARRAY",
          createdBitmapIndex: true
        };
        newDims.push(ob1);
        updatedRow = true;
      }
    });

    parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions = [
      ...parsedJSONSpec.spec.dataSchema.dimensionsSpec.dimensions,
      ...newDims
    ];

    return JSON.stringify(parsedJSONSpec, null, 2);
    //JSON.stringify(JSON.parse(druidIngestionSpec), null, 2)
    //this.setState({ ...this.state, spec: JSON.stringify(parsedJSONSpec) });
  };


  render() {
    const { spec } = this.state;

    let datasetDetails = this.state.datasetDetails;
    const isDatasetPublished = datasetDetails.isPublishedToDruid;

    let druidIngestionSpec = !_.isNil(datasetDetails.druidIngestionSpec)
      ? JSON.stringify(JSON.parse(datasetDetails.druidIngestionSpec), null, 2)
      : JSON.stringify({});

    druidIngestionSpec =
      !_.isNil(spec) && spec.length > 0
        ? JSON.stringify(JSON.parse(spec), null, 2)
        : druidIngestionSpec;

    let measuresAndDimensions = this.getDimensionsAndMeasuresTable(
      druidIngestionSpec,
      datasetDetails,
      isDatasetPublished
    );

    druidIngestionSpec = this.updateCurrentDruidIngestionSpec(
      druidIngestionSpec,
      datasetDetails
    );
    //druidIngestionSpec = JSON.stringify(JSON.parse(druidIngestionSpec), null, 2)

    let updatedDatasetDetails = _.isNil(measuresAndDimensions)
      ? []
      : measuresAndDimensions["mappedColumns"];
    let isSchemaUpdated = _.isNil(measuresAndDimensions)
      ? false
      : measuresAndDimensions["isSchemaUpdated"];

    const options = [
      { value: "string", label: "string" },
      { value: "double", label: "double" },
      { value: "long", label: "long" }
      // { value: 'timestamp', label: 'timestamp' }
    ];

    const columns = [
      {
        title: "Source Column",
        dataIndex: "columnName",
        key: "columnName",
        width: "25%"
      },
      {
        title: "Source Data Type",
        dataIndex: "dremioDataType",
        key: "dremioDataType",
        width: "25%"
      },
      {
        title: "Destination Data Type",
        dataIndex: "druidDataType",
        key: "druidDataType",
        width: "20%",
        render: (text, record) => {
          let defaultValue = { value: text, label: text };
          let elem = (
            <RSelect
              options={options}
              defaultValue={defaultValue}
              onChange={newValue =>
                this.onChangeDruidDataType(newValue, record, druidIngestionSpec)
              }
            />
          );
          return elem;
        }
      },
      {
        title: "Type",
        dataIndex: "columnType",
        key: "columnType",
        width: "30%",
        align: "left",
        render: (text, record) => {
          let elem = (
            <Radio.Group
              onChange={event =>
                this.onChangeDruidColumnType(event, record, druidIngestionSpec)
              }
              value={text}
            >
              <Row>
                <Col>
                  <Radio value="measure">Measure</Radio>
                </Col>
                <Col>
                  <Radio value="dimension">Dimension</Radio>
                </Col>
                <Col>
                  <Radio value="timestamp">Timestamp </Radio>
                </Col>
              </Row>
            </Radio.Group>
          );
          return elem;
        }
      }
    ];

    let element = <div />;

    if (datasetDetails.dremioSchema) {
      element = (
        <div>
          <Row>
            <Col span={24} style={{ padding: "10px" }}>
              <span>
                <div
                  style={{
                    display: "inline",
                    float: "left",
                    padding: "right 10px"
                  }}
                >
                </div>
                <div
                  style={{
                    display: "inline",
                    float: "right",
                    padding: "right 10px",
                    cursor: "pointer"
                  }}
                >
                  {/* <b> Published: {showPublished}</b> &nbsp;&nbsp; */}
                  <Button type="link" onClick={this.showModal}>
                    View spec
                  </Button>
                  <Button
                    type="primary"
                    size="small"
                    onClick={() =>
                      this.verifySchema(druidIngestionSpec)
                    }
                    disabled={this.state.schemaVerified}
                  >
                    Verify
                  </Button>
                  &nbsp;&nbsp;
                  <Button
                    type="primary"
                    size="small"
                    onClick={this.clearSchema}
                  >
                    Cancel
                  </Button>{" "}
                  &nbsp;&nbsp;
                </div>

                <Modal
                  title="Druid Ingestion Spec"
                  visible={this.state.visible}
                  onOk={this.handleCancel}
                  onCancel={this.handleCancel}
                >
                  <AceEditor
                    style={{ width: "100%", height: "400px" }}
                    mode="json"
                    readOnly
                    theme="github"
                    name="UNIQUE_ID_OF_DIV"
                    value={druidIngestionSpec}
                    editorProps={{ $blockScrolling: true }}
                  />
                </Modal>
              </span>
              <br />
              <Table
                scroll={{ x: "100%" }}
                columns={columns}
                dataSource={updatedDatasetDetails}
                pagination={false}
                rowKey="columnName"
              />
            </Col>
          </Row>
        </div>
      );
    }
    return (
      <div>
        <div>
        <Input type={"text"} value={this.state.datasetLocation} onChange={this.handleDatasetChange}/>
        </div>
        <br />
        <div>
        Datasource Name
        <Input type={"text"} value={this.state.datasourceName} onChange={e => {this.setState({datasourceName: e.target.value})}}/>
        </div>
        <br />
        <div>       
        <Button
            type="primary"
            size="small"
            onClick={this.fetchSchema}
            >
            Get schema
        </Button>
        </div>
        {element}
      </div>
    );
  }
}

export default DatasetSelector;
