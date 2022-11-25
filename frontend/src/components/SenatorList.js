import { Component } from 'react';
import "./SenatorList.css";
import React from 'react';

class Header extends Component {
  render() {
    return (
      <div className="senatorlist_header">Senators</div>
    )
  }
}

class Stat extends Component {
  render() {
    if (this.props.value !== 0) {
      return (
        <div className="senatorlist_stat">{this.props.value}</div>
      );
    } else {
      return (
        <div className="senatorlist_stat"></div>
      );
    }
    
  }
}

class ListSenator extends Component {
  renderMajorOffice = () => {
    if (this.props.senator["majoroffice"] !== null) {
      return (
        <div className='senatorlist_senator_office'>
          <div className="majoroffice">
            {this.props.senator["majoroffice"]}
          </div>
          <div>{this.props.senator["rank"]}</div>
        </div>
      );
    } else {
      return (
        <div className='senatorlist_senator_office'></div>
      );
    }
  }

  renderBanner = () => {
    if (this.props.senator["faction"] !== null) {
      const color = this.props.senator["faction"]
      return (
        <div className='senatorlist_senator_banner'>
          <div style={{backgroundColor: color}}></div>
          <div>7</div>
        </div>
      );
    } else {
      return (
        <div className='senatorlist_senator_banner'>
          <div style={{backgroundColor: 'white'}}></div>
          <div>7</div>
        </div>
      );
    }
  }

  render() {
    return (
      <div className="senatorlist_senator">
        {this.renderMajorOffice()}
        {this.renderBanner()}
        <div className='senatorlist_senator_portait'></div>
        <div className='senatorlist_senator_mainsection'>
          <div>{this.props.senator["name"]}</div>
          <div className="senatorlist_senator_titleandlocation">
            <div>
              <span className='bluelink'>{this.props.senator["title"]}</span>
              &nbsp;at&nbsp;
              <span className='bluelink'>{this.props.senator["location"]}</span>
            </div>
            
          </div>
          <div className="senatorlist_statrow">
            <Stat key="military" value={this.props.senator["military"]} />
            <Stat key="oratory" value={this.props.senator["oratory"]} />
            <Stat key="loyalty" value={this.props.senator["loyalty"]} />
            <Stat key="knights" value={this.props.senator["knights"]} />
            <Stat key="influence" value={this.props.senator["influence"]} />
            <Stat key="popularity" value={this.props.senator["popularity"]} />
            <Stat key="talents" value={this.props.senator["talents"]} />
          </div>
        </div>
      </div>
    );
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
    const response = await fetch("sampledata\\Senators.json", {
      headers : { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
       }
    });
    const data = (await response.json())["senators"];
    return data;
  }

  render() {
    return (
      <div className="senatorlist">
        <Header />
        <div className='senatorlist_scrollarea'>
          {this.state.senators.map(s => <ListSenator key={s["name"]} senator={s} />)}
        </div>
      </div>
    );
  }
}

export default SenatorList;
