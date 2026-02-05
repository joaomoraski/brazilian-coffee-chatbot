import CoffeeIcon from "@/components/ui/CoffeeIcon";

export default function ChatHeader() {
  return (
    <header className="bg-coffee-primary text-white py-4 px-6 shadow-lg">
      <div className="max-w-4xl mx-auto flex items-center gap-3">
        <CoffeeIcon size={36} className="text-coffee-secondary" animated />
        <div>
          <h1 className="text-xl font-bold tracking-tight">
            Brazilian Coffee Chatbot
          </h1>
          <p className="text-coffee-senary text-sm">
            Your guide to Brazilian coffee culture
          </p>
        </div>
      </div>
    </header>
  );
}
