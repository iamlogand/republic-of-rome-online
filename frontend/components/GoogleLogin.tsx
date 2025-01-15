import Image from "next/image"

interface GoogleLoginProps {
  onClick: () => void
}

const GoogleLogin = ({ onClick }: GoogleLoginProps) => {
  return (
    <button onClick={onClick}>
      <Image
        src="\googleLogin.svg"
        height={42}
        width={200}
        alt="Continue with Google"
      />
    </button>
  )
}

export default GoogleLogin
