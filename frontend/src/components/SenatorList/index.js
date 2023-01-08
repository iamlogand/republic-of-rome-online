import { Component } from 'react';
import "../../css/SenatorList.css";
import React from 'react';
import Header from "./Header.js"
import Senator from "./Senator.js"

/**
 * This is the root component for the `SenatorList` group.
 * Contains one `Header` and zero or many `Senator` instances
 */
class List extends Component {
  constructor(props) {
    super(props);
    this.state = {
      senators: [],
      hoverCol: ""
    };
    this.componentDidMount = this.componentDidMount.bind(this);
  }

  componentDidMount = async () => {
    this.setState({ senators: await this.getSenators() });
  }

  getSenators = async () => {
    const response = await fetch("sampledata\\Senators.json", {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    const data = (await response.json())["senators"];
    return data;
  }

  setHoverCol = (name) => {
    this.setState({hoverCol: name});
  }

  render = () => {
    return (
      <div className="senator-list">
        <Header
          hoverCol={this.state.hoverCol}
          setHoverCol={this.setHoverCol}/>
        <div className='senator-list_scroll-area'>
          {this.state.senators.map(s => <Senator
            key={s["name"]}
            senator={s}
            hoverCol={this.state.hoverCol}
            setHoverCol={this.setHoverCol} />)}
        </div>
      </div>
    );
  }
}

export default List;
