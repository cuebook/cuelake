import React from "react";
import { Button, Form, Input } from "antd";
import style from "./style.module.scss";

class Update extends React.Component {
  constructor() {
    this.state = {
      con: null,
      conType: null
    };
    this.count = 1;
  }

  componentDidMount() {
    const { dispatch, match } = this.props;
    dispatch({
      type: "connections/SET_STATE",
      payload: { connections: [], connectionTypes: [] }
    });
    dispatch({
      type: "connections/LOAD_CONNECTION",
      payload: match.params.connectionId
    });
    dispatch({
      type: "connections/LOAD_CONNECTIONTYPES"
    });
  }

  componentWillReceiveProps(props) {
    const cons = props.connections;
    let con = cons.selectedConnection;
    if (con && cons.connectionTypes.length) {
      const conType = cons.connectionTypes.filter(
        item => item.id === con.connectionTypeId
      )[0];
      this.setState({ conType: conType, con: con });
    }
  }

  handleSubmit() {
    const { dispatch, form } = this.props;
    form.validateFields((error, values) => {
      // additional user confirmation if any queries use this connection
      if (this.state.con.queryCount) {
        const val = window.confirm(
          `${this.state.con.queryCount} queries alredy use these details`
        );
      }

      if (!error) {
        let temp = { ...values };
        delete temp["title"];
        let params = [];
        for (let key in temp) {
          params.push({ paramId: key, paramValue: temp[key] });
        }

        let payload = {
          title: values["title"],
          description: "",
          connectionType_id: this.state.conType.id,
          params: params
        };

        // send connection id
        // append server type

        dispatch({
          type: "connections/UPDATE_CONNECTION",
          payload: {
            connection_id: this.props.match.params.connectionId,
            payload: payload
          }
        });
      }
    });
  }

  render() {
    const { form, connections, match } = this.props;

    if (this.props.connections.loading || this.props.connections.typeLoading) {
      return <h2> LOADING... </h2>;
    }

    if (!this.state.con || !connections.connectionTypes.length) {
      return <h2>404 NOT FOUND</h2>;
    }

    let paramItems = !this.state.conType
      ? null
      : this.state.conType.params.map(item => {
          let prop = null;
          // if (item.properties != null && item.properties != "") {
          //   prop = JSON.parse(item.properties);
          // }
          let properties_param = JSON.parse(item.properties);

          return properties_param.type === "password" ? (
            <div
              style={{ width: properties_param.width }}
              className={style.inputGroup}
            >
              <Form.Item hasFeedback key={item}>
                {form.getFieldDecorator(item.id.toString(), {
                  ...prop,
                  initialValue: this.state.con.params[item.paramName],
                  rules: [properties_param !== "" ? properties_param.rules : ""]
                })(
                  <Input
                    type={item.isEncrypted ? "password" : properties_param.type}
                    className={style.inputArea}
                  />
                )}
                <label className={style.label}>
                  {item.paramName.charAt(0).toUpperCase() +
                    item.paramName.slice(1)}
                </label>
              </Form.Item>
            </div>
          ) : (
            <div
              style={{ width: properties_param.width }}
              className={style.inputGroup}
            >
              <Form.Item hasFeedback key={item}>
                {form.getFieldDecorator(item.id.toString(), {
                  ...prop,
                  initialValue: this.state.con.params[item.paramName],
                  rules: [properties_param !== "" ? properties_param.rules : ""]
                })(
                  <Input
                    id={item.id.toString()}
                    type={item.isEncrypted ? "password" : properties_param.type}
                    className={style.inputArea}
                  />
                )}
                <label for={item.id.toString()} className={style.label}>
                  {item.paramName.charAt(0).toUpperCase() +
                    item.paramName.slice(1)}
                </label>
              </Form.Item>
            </div>
          );
        });

    let formDisplay = (
      <Form layout="vertical" hideRequiredMark className="mb-2 ">
        <div class="row">
          <div style={{ width: "49%" }} className={style.inputGroup}>
            <Form.Item hasFeedback>
              {form.getFieldDecorator("title", {
                initialValue: this.state.con.title,
                rules: [
                  {
                    required: true,
                    message: "Please enter Connection Name!"
                  }
                ]
              })(
                <Input
                  id="inp1"
                  type="text"
                  required
                  className={style.inputArea}
                />
              )}
              <label for="inp1" className={style.label}>
                Connection Name
              </label>
            </Form.Item>
          </div>
          &nbsp;
          <div style={{ width: "49%" }} className={style.inputGroup}>
            <Form.Item>
              <Input
                value={this.state.conType.name}
                disabled
                style={{ backgroundColor: "white" }}
                className={style.inputArea}
              />
              <label className={style.label}>Connection Type</label>
            </Form.Item>
          </div>
          {paramItems}
        </div>
        <hr style={{ marginLeft: "-2%" }} />
        <Button
          type="primary"
          className="mr-2"
          onClick={() => this.handleSubmit()}
        >
          SAVE
        </Button>
      </Form>
    );

    return (
      <div>
        <div className="row " ref={this.appref}>
          <div className="col-md-8 card offset-md-2 shadow-sm bg-white p-5 mb-5 rounded">
            <div className={style.flexBox}>
              <img
                className={style.logoStyle}
                // src={require("assets/media/" +
                //   this.state.conType.name +
                //   ".png")}
                alt={this.state.conType.name}
              />
              <h4 style={{ fontWeight: "100" }}>Connection Settings</h4>
            </div>
            <hr style={{ marginLeft: "-2%" }} />
            <br />
            <div>{formDisplay}</div>
          </div>
        </div>
      </div>
    );
  }
}

export default Update;
