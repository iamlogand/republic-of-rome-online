import { Link } from "react-router-dom";
import TitleBanner from "../components/TitleBanner.js";
import "./Home.css";
import LoginForm from "../components/LoginForm.js";


export default function LoginPage(props) {
  return (
    <div>
      <TitleBanner />
      <div className='back'>
        <Link to="..">Back to Main Menu</Link>
      </div>
      <LoginForm setAccessToken={props.setAccessToken} />
    </div>
  )
}