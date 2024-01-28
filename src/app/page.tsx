import { Inter } from 'next/font/google'
import data from '../../data/data';
import { ImInstagram } from "react-icons/im";
const inter = Inter({ subsets: ['latin'] })

export default function Home() {
  const currentYear = new Date().getFullYear()
  const {
    sitename,
    sitetagline,
    description,
    copyrightText,
    newsletterheading,
    socialIcons,
    socialIconsHeading,
    title,
  } = data

  return (
    <>
      <main className="flex min-h-screen flex-col items-center justify-between p-5 lg:p-12">
        <div className="z-10 w-full max-w-5xl items-center justify-between text-sm ">

          <div className=" bottom-0 left-0 flex h-30 md:h-48 w-full items-end justify-center  lg:static lg:h-auto lg:w-auto lg:bg-none">
            <a
              className="pointer-events-none flex place-items-center gap-2 p-4 lg:pointer-events-auto lg:p-0"
              href="/"
              rel="noopener noreferrer"
            >
              <div className='flex flex-col text-center'>
                <h1 className='text-2xl lgtext-4xl text-sky-400/100 font-semibold	'> {sitename} </h1>
              </div>
            </a>
          </div>
        </div>

        <div className="relative flex flex-col  place-items-center ">
          <h2 className='text-center font-heading m-10 text-6xl sm:text-7xl lg:text-8xl leading-[5rem] sm:leading-[7rem] lg:leading-[7rem] font-black	 '>
            <span className='bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500'>{title}</span>
            <span className=''>⏳</span>
          </h2>
          <p className='text-2xl md:text-3xl px-6 max-w-3xl text-center m-5 text-slate-800 dark:text-slate-100 font-thin' dangerouslySetInnerHTML={{
            __html: description
          }}>
          </p>
        </div>

      <div className='text-center lg:m-7 mt-10 w-80 p-3' >
              <label htmlFor="email" className="block text-slate-800 dark:text-slate-100  font-light text-sm leading-6">{newsletterheading}</label>
              <div className='my-4 text-center' >
                <ul className='flex flex-wrap lg:flex justify-center '>
                  <li className='px-2'> {socialIconsHeading} </li>
                  {socialIcons.map((social, index) =>
                  (
                    <li key={index} className='px-2 capitalize border-1  hover:border-b-white'>
                      <a target='_blank' className='' href={social.link}> 
                        <ImInstagram className='text-2xl' color='white' />
                      </a>
                    </li>
                  )
                  )}
                </ul>
              </div>
        </div>

        <footer className='text-slate-500 text-center'>
          
          <div className=''>
            <p className='' dangerouslySetInnerHTML={{
              __html: copyrightText
            }}>
            </p>

          </div>
        </footer>

      </main>
    </>
  )
}
