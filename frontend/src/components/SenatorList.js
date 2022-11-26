import { Component } from 'react';
import "./SenatorList.css";
import React from 'react';
import { Link } from "react-router-dom";

class Header extends Component {
  render = () => {
    return (
      <div className="senatorlist_header">
        <div className="senatorlist_header_office"><div>Major Office</div></div>
        <div className="senatorlist_header_banner"><div className="senatorlist_banner" style={{ backgroundColor: 'white' }}></div></div>
        <div className="senatorlist_header_aboveportrait"></div>
        <Stat key="military" colName="military" title="Mil"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="oratory" colName="oratory" title="Ora"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="loyalty" colName="loyalty" title="Loy"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="knights" colName="knights" title="Kni"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="influence" colName="influence" title="Inf"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="popularity" colName="popularity" title="Pop"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="talents" colName="talents" title="Tal"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <div className="senatorlist_misc senatorlist_header_misc">Miscellaneous</div>
      </div>
    )
  }
}

class Stat extends Component {
  constructor(props) {
    super(props);
    this.state = {
      style: this.getStyle(),
      prefix: this.getPrefix()
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.hoverCol !== prevProps.hoverCol) {
      this.setState({style: this.getStyle()})
    }
  }

  mouseEnter = () => {
    this.props.setHoverCol(this.props.colName);
  }

  mouseLeave = () => {
    if (this.state.hoverCol !== this.props.colName) {
      this.props.setHoverCol('');
    }
  }

  getStyle = () => {
    let style = {};
    if (this.props.colName === this.props.hoverCol) {
      Object.assign(style, { color: 'white', backgroundColor: '#696969'});
    }
    if (this.props.type === "realint") {
      if (this.props.value > 0) {
        Object.hasOwn(style, 'backgroundColor') ? Object.assign(style, {color: '#cce5cc'}) : Object.assign(style, {color: 'green'});
      } else if (this.props.value < 0) {
        Object.hasOwn(style, 'backgroundColor') ? Object.assign(style, {color: '#ffb2b2'}) : Object.assign(style, {color: 'red'});
      }
    }
    return style;
  }

  getPrefix = () => {
    if (this.props.type === "realint") {
      if (this.props.value > 0) {
        return '+';
      } else if (this.props.value < 0) {
        return null;
      }
    } else {
      return null
    }
  }

  render = () => {
    if (typeof this.props.title !== "undefined") {
      return (
        <div className="senatorlist_stat noselect"
          onMouseEnter={this.mouseEnter} onMouseLeave={this.mouseLeave}
          style={this.state.style}>{this.props.title}</div>
      );
    }
    if (this.props.value !== 0) {
      return (
        <div className="senatorlist_stat noselect"
          onMouseEnter={this.mouseEnter} onMouseLeave={this.mouseLeave}
          style={this.state.style}>{this.state.prefix}{this.props.value}</div>
      );
    } else {
      return (
        <div className="senatorlist_stat noselect"
          onMouseEnter={this.mouseEnter} onMouseLeave={this.mouseLeave}
          style={this.state.style}></div>
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
          <div className='senatorlist_banner' style={{ backgroundColor: color }}></div>
          {this.renderVotes()}
        </div>
      );
    } else {
      return (
        <div className='senatorlist_senator_banner'>
          <div className='senatorlist_banner' style={{ backgroundColor: 'white' }}></div>
          {this.renderVotes()}
        </div>
      );
    }
  }

  renderVotes = () => {
    const voteCount = this.props.senator["oratory"] + this.props.senator["knights"]
    return (
      <div>{voteCount}</div>
    );
  }

  renderType = () => {
    if (this.props.senator["family"] === true && this.props.senator["statesman"] === true) {
      return (
        <div className='senatorlist_senator_nameandtype'>
          <Link className='bluelink no_decor hover_decor'>Statesman</Link>
          <br />and&nbsp;
          <Link className='bluelink no_decor hover_decor'>Family</Link>
        </div>
      );
    }
    if (this.props.senator["statesman"] === true) {
      return (
        <div className='senatorlist_senator_nameandtype'>
          <Link className='bluelink no_decor hover_decor'>Statesman</Link>
        </div>
      );
    } else {
      return (
        <div className='senatorlist_senator_nameandtype'>
          <Link className='bluelink no_decor hover_decor'>Family</Link>
        </div>
      );
    }
  }

  renderItems = () => {
    if (this.props.senator["items"] > 0) {
      const items = []
      for (let i = 1; i <= this.props.senator["items"]; i++) {
        items.push({ name: i });
      }
      return (
        <div>
          {items.map(i => <div key={i.name} className='senatorlist_senator_item'>{i.name}</div>)}
        </div>
      );
    } else {
      return (
        <div></div>
      );
    }
  }

  render = () => {
    return (
      <div className="senatorlist_senator">
        {this.renderMajorOffice()}
        {this.renderBanner()}
        <div className='senatorlist_senator_portait'></div>
        <div className='senatorlist_senator_mainsection'>
          <div className="senatorlist_senator_textarea">
            <div>
              <div><Link className='bluelink no_decor hover_decor'>{this.props.senator["name"]}</Link></div>
              {this.renderType()}
            </div>
            <div className="senatorlist_senator_titleandlocation">
              <div>
                <Link className='bluelink no_decor hover_decor'>{this.props.senator["title"]}</Link>
                &nbsp;at&nbsp;
                <Link className='bluelink no_decor hover_decor'>{this.props.senator["location"]}</Link>
              </div>
            </div>
          </div>
          <div className="senatorlist_statrow">
            <Stat key="military" colName="military" value={this.props.senator["military"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
            <Stat key="oratory" colName="oratory" value={this.props.senator["oratory"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
            <Stat key="loyalty" colName="loyalty" value={this.props.senator["loyalty"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
            <Stat key="knights" colName="knights" value={this.props.senator["knights"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
            <Stat key="influence" colName="influence" value={this.props.senator["influence"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
            <Stat key="popularity" colName="popularity" value={this.props.senator["popularity"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol}
              type="realint" />
            <Stat key="talents" colName="talents" value={this.props.senator["talents"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
          </div>
        </div>
        <div className="senatorlist_misc">
          {this.renderItems()}
        </div>
      </div>
    );
  }
}

class SenatorList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      senators: [],
      hoverCol: "knights"
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
      <div className="senatorlist">
        <Header
          hoverCol={this.state.hoverCol}
          setHoverCol={this.setHoverCol}/>
        <div className='senatorlist_scrollarea'>
          {this.state.senators.map(s => <ListSenator
            key={s["name"]}
            senator={s}
            hoverCol={this.state.hoverCol}
            setHoverCol={this.setHoverCol} />)}
        </div>
      </div>
    );
  }
}

export default SenatorList;
