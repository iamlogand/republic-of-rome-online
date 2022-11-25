import { Component } from 'react';
import "./SenatorList.css";

class Title extends Component {
  render() {
    return (
      <div className="senatorlist_header">Senators</div>
    )
  }
}

class Senator extends Component {
  render() {
    return (
      <div className="senatorlist_senator">{this.props.name}</div>
    )
  }
}

class SenatorList extends Component {
  constructor(props) {
    super(props);
    this.state = { senators: [] };
    this.componentDidMount = this.componentDidMount.bind(this);
  }

  async componentDidMount() {
    this.setState({ senators: await this.getSenators() });
  }

  getSenators = async () => {
    const response = await fetch("mockdata\\Senators.json", {
      headers : { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
       }
    });
    const data = (await response.json())["senators"];
    console.log(data);
    return data;
  }

  render() {
    return (
      <div className="senatorlist">
        <Title />
        {this.state.senators.map(s => <Senator key={s} name={s} />)}
      </div>
    );
  }
}

export default SenatorList;
