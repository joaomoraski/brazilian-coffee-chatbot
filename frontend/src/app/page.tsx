import ChatContainer from "@/components/Chat/ChatContainer";
import ChatHeader from "@/components/Chat/ChatHeader";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <ChatHeader />
      <div className="flex-1 flex justify-center px-4 py-6">
        <div className="w-full max-w-4xl">
          <ChatContainer />
        </div>
      </div>
    </main>
  );
}
