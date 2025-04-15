import { Roboto } from "next/font/google"
import Image from "next/image"

const roboto = Roboto({
  weight: "500",
  subsets: ["latin"],
  display: "swap",
})

interface GoogleLoginProps {
  onClick: () => void
}

const GoogleLogin = ({ onClick }: GoogleLoginProps) => {
  return (
    <div>
      <button
        onClick={onClick}
        className="flex h-10 items-center gap-2.5 rounded border border-[#747775] px-3 py-2.5"
      >
        <Image
          src="/googleIcon.png"
          height={20}
          width={20}
          alt="Continue with Google"
        />
        <span
          className={`text-sm font-[500] text-[#1F1F1F] ${roboto.className}`}
        >
          Continue with Google
        </span>
      </button>
    </div>
  )
}

export default GoogleLogin
