import { Component } from 'react';
import "../../css/SenatorList.css";
import React from 'react';
import { Link } from "react-router-dom";
import Stat from "./Stat.js"

class Senator extends Component {
  renderMajorOffice = () => {
    if (this.props.senator["majorOffice"] !== null) {
      return (
        <div className='senator-list_senator_office'>
          <div className="majorOffice">
            {this.props.senator["majorOffice"]}
          </div>
          <div>{this.props.senator["rank"]}</div>
        </div>
      );
    } else {
      return (
        <div className='senator-list_senator_office'></div>
      );
    }
  }

  renderBanner = () => {
    if (this.props.senator["faction"] !== null) {
      const color = this.props.senator["faction"]
      return (
        <div className='senator-list_senator_banner'>
          <div className='senator-list_banner' style={{ backgroundColor: color }}></div>
          {this.renderVotes()}
        </div>
      );
    } else {
      return (
        <div className='senator-list_senator_banner'>
          <div className='senator-list_banner' style={{ backgroundColor: 'white' }}></div>
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
        <div className='senator-list_senator_name-and-type'>
          <Link className='bluelink no_decor hover_decor'>Statesman</Link>
          <br />and&nbsp;
          <Link className='bluelink no_decor hover_decor'>Family</Link>
        </div>
      );
    }
    if (this.props.senator["statesman"] === true) {
      return (
        <div className='senator-list_senator_name-and-type'>
          <Link className='bluelink no_decor hover_decor'>Statesman</Link>
        </div>
      );
    } else {
      return (
        <div className='senator-list_senator_name-and-type'>
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
          {items.map(i => <div key={i.name} className='senator-list_senator_item'>{i.name}</div>)}
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
      <div className="senator-list_senator">
        {this.renderMajorOffice()}
        {this.renderBanner()}
        <div className='senator-list_senator_portrait'></div>
        <div className='senator-list_senator_main-section'>
          <div className="senator-list_senator_textarea">
            <div>
              <div><Link className='bluelink no_decor hover_decor'>{this.props.senator["name"]}</Link></div>
              {this.renderType()}
            </div>
            <div className="senator-list_senator_title-and-location">
              <div>
                <Link className='bluelink no_decor hover_decor'>{this.props.senator["title"]}</Link>
                &nbsp;at&nbsp;
                <Link className='bluelink no_decor hover_decor'>{this.props.senator["location"]}</Link>
              </div>
            </div>
          </div>
          <div className="senator-list_stat-row">
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
              type="realInt" />
            <Stat key="talents" colName="talents" value={this.props.senator["talents"]}
              hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
          </div>
        </div>
        <div className="senator-list_misc">
          {this.renderItems()}
        </div>
      </div>
    );
  }
}

export default Senator;
