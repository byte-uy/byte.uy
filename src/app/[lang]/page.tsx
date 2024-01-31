import Navigation from '@/app/ui/navigation'

export default async function IndexPage({
  params: { lang },
}: {
  params: { lang: string };
}) {
  return (
    <Navigation /> 
  )
}
