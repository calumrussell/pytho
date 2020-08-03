import React from "react"

import { Button, PlusIcon } from './common.js'

export class PortfolioShareInput extends React.Component {

  constructor(props){
    super(props)
    this.state = {
      security: '',
      allocation: '' 
    }
    this.inputChange = this.inputChange.bind(this)
    this.inputSubmit = this.inputSubmit.bind(this)
  }

  inputSubmit(e) {
    e.preventDefault()
    const { security, allocation } = this.state
    if (security == '' || allocation == ''){
      return
    }

    this.props.addSecurity(this.state)
    this.setState({
      security: '',
      allocation: '' 
    })
  }

  inputChange(e) {
    e.preventDefault()
    const { value, name } = e.target
    this.setState({[name]: value})
  }

  render() {
    const { onSubmitFunc } = this.props
    const { security, allocation } = this.state
    return (
      <form id="portfolioshare-input">
        <label>
          Input security:
          <input
            type="text"
            aria-label="security-input"
            name={'security'}
            value={security}
            onChange={this.inputChange} />
        </label>
        <label>
          Input weight:
          <input
            type="text"
            aria-label="weight-input"
            name={'allocation'}
            value={allocation}
            onChange={this.inputChange} />
        </label>
        <Button
          type={'icon'}
          onClickFunc={this.inputSubmit}>
          <PlusIcon />
        </Button>
        <div>
          Can input portfolio as £ or % amounts
        </div>
     </form>
    )
  }
}
