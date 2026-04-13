import TeacherSidebar from '@/components/TeacherSidebar'
import TeacherMobileBar from '@/components/TeacherMobileBar'

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <TeacherSidebar />
      <div className="flex-1 min-w-0 flex flex-col">
        <TeacherMobileBar />
        <div className="flex-1">{children}</div>
      </div>
    </div>
  )
}
